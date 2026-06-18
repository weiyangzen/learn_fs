# sources/cloud-native/cri-o/internal/config/blockio/blockio.go

## Purpose
BlockIO config loader wrapping Intel goresctrl blockio configuration.

## Important APIs, Types, and Functions
Config tracks enabled, reload flag, cleaned path, and *blockio.Config. New initializes empty config. Enabled, SetReload, ReloadRequired are accessors. Reload reads YAML path, unmarshals into blockio.Config, calls blockio.SetConfig(tmpCfg,true), and stores it. Load resets state, cleans path, reloads, logs, and enables.

## Control Flow
Load with empty path disables blockio. Load with path reads/validates/applies immediately. Reload re-reads stored path and rescans devices.

## State and Persistence
Holds in-memory config/path/reload flags; blockio.SetConfig mutates global goresctrl blockio state and scans host devices.

## Dependencies
Depends on os, sigs.k8s.io/yaml, github.com/intel/goresctrl/pkg/blockio, logrus.

## Integration Points
Integrated with CRI-O config reload and workload class assignment.

## Risks and Edge Cases
Invalid YAML leaves enabled false; Reload after path set can partially affect global blockio before error depending library; host device topology matters.

## Test Signals
blockio_test.go covers empty/new, missing file, invalid schema, and valid config.
