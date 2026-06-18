# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/constants.h

## Purpose

`constants.h` centralizes tunable MLD policy constants for beacon-loss thresholds, power-save timers, scan/listen parameters, RSSI thresholds, EMLSR defaults, D3/debug options, FTM defaults, and extended capability sizes.

## Important APIs, Types, and Functions

It defines macros such as missed-beacon thresholds, power-save TX/RX data timeouts, snooze/heavy-traffic thresholds, passive scan timeouts, connection listen interval, EMLSR toggles and thresholds, FTM initiator algorithm/parameter defaults, and `IWL_MLD_STA_EXT_CAPA_SIZE`.

## Control Flow

There is no executable control flow. Other MLD components compile these values into power, scan, MLO, FTM, D3, and AP behavior.

## State and Persistence Behavior

The constants are compile-time policy, not runtime state. They indirectly shape firmware commands and driver decisions in many source files.

## Dependencies and Integration Points

The file is included by MLD modules that need shared defaults, including FTM initiator code. Values refer to firmware API constants such as `IWL_TOF_ALGO_TYPE_MAX_LIKE` through the broader include graph.

## Risks and Edge Cases

There is a duplicate definition of `IWL_MLD_PS_SNOOZE_INTERVAL`, currently identical but still a maintenance smell. Policy values are opaque and not runtime-configurable, so tuning requires rebuilds. Changing thresholds can alter roaming, scan, power, and EMLSR behavior across the driver.

## Test Signals

Build with warnings for macro redefinition, run power-save and EMLSR behavioral tests after threshold changes, and validate FTM requests still encode supported defaults.
