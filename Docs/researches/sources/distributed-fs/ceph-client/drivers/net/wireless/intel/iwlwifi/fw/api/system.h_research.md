# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/api/system.h

## Purpose
Defines small system-level firmware configuration commands for SOC latency/stabilization and feature disablement.

## Important APIs, Types, And Functions
Constants define SOC configuration flags for discrete device mode and low latency, plus LTR apply-delay masks/values. `struct iwl_soc_configuration_cmd` carries SOC flags and stabilization latency. `struct iwl_system_features_control_cmd` carries a four-dword bitmap of features to disable.

## Control Flow
There is no local execution. During device initialization or feature negotiation, the driver sends SOC configuration to communicate platform latency and power-stability constraints, and may send system feature control to disable firmware features by bitmap.

## State And Persistence
Firmware persists the applied SOC and feature settings until reset or reconfiguration. The header itself is stateless. Version 1 of SOC configuration treats `flags` as a whole integer with only the discrete flag available, while version 2 permits independent bits.

## Dependencies And Integration Points
Uses kernel bit and little-endian types. It integrates with iwlwifi transport/device initialization, platform power management, latency tolerance reporting, and firmware capability gating.

## Risks
The version-specific interpretation of `flags` is easy to misuse: setting newer independent bits against a version-1 command can change the integer value in a way firmware does not expect. Incorrect latency values or LTR delay selection can affect power sequencing, wake latency, or XTAL stability.

## Test Signals
Boot devices across integrated and discrete platforms, verify firmware accepts SOC configuration, check low-latency mode behavior, and confirm disabled feature bitmaps produce expected capability changes without firmware asserts.
