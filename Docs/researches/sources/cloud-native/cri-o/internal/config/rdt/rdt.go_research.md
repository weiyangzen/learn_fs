# sources/cloud-native/cri-o/internal/config/rdt/rdt.go

Purpose: manages CRI-O Intel RDT/resctrl configuration loading and container class lookup.

Important APIs/types/functions: constants `DefaultRdtConfigFile` and `ResctrlPrefix`; `Config` with `supported`, `enabled`, and `*rdt.Config`; `New`, `Supported`, `Enabled`, `Load`, `loadConfigFile`, and `ContainerClassFromAnnotations`.

Control flow: `New` sets the goresctrl logger, calls `rdt.Initialize`, and marks support false if initialization fails. `Load` disables the feature by default, exits successfully if unsupported or path is empty, reads YAML config, calls `rdt.SetConfig(tmpCfg, true)`, logs success, and stores the config while enabling RDT. `ContainerClassFromAnnotations` delegates class resolution to goresctrl and rejects non-empty classes when CRI-O RDT is disabled.

State and persistence behavior: loads YAML from disk and stores the parsed config in memory. It also configures goresctrl global RDT state through `Initialize` and `SetConfig`.

Dependencies/integration points: depends on `github.com/intel/goresctrl/pkg/rdt`, `sigs.k8s.io/yaml`, slog, and logrus. Container creation paths can use annotation-derived classes from this config.

Risks: host RDT support and resctrl mount state are external. Loading a config mutates global goresctrl state. Empty default path means RDT is opt-in.

Test signals: `rdt_test.go` covers missing files, invalid YAML shape, and a minimal valid config for `loadConfigFile`.
