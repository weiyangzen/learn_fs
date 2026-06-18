# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/api/sf.h

## Purpose
Defines the Smart FIFO firmware configuration ABI. Smart FIFO tunes RX FIFO watermarks and aging/idle timers for power/performance behavior across traffic scenarios.

## Important APIs, Types, And Functions
`enum iwl_sf_state` describes Smart FIFO operating states such as full-on, uninitialized, and init-off. `enum iwl_sf_scenario` covers unicast, aggregation, multicast, BA response, and TX response scenarios. Constants define default and BSS-specific watermarks/timers. `struct iwl_sf_cfg_cmd` is the packed command sent to firmware with state, watermarks, and timeout matrices.

## Control Flow
There is no local execution. Callers choose a Smart FIFO state and timer profile based on interface mode and activity, then send `iwl_sf_cfg_cmd` to firmware. Firmware applies the selected transient-state watermarks and per-scenario timeout values to RX FIFO handling.

## State And Persistence
The header stores no state. Firmware persists the configured Smart FIFO state until reconfigured, reset, or device restart. The command embeds two transient watermarks and two timer values for each scenario, so partial initialization bugs can affect multiple traffic classes.

## Dependencies And Integration Points
Uses bit macros and little-endian types from the kernel environment. It integrates with iwlwifi power management and RX buffering decisions, especially BSS configuration and scan/powersave transitions.

## Risks
Timer comments mix microsecond and millisecond wording, so callers should treat constants as firmware-defined units aligned to 32 usec rather than infer from comments. Incorrect watermarks can starve RX buffering or waste power. `SF_LONG_DELAY_ON` is documented as not driver-called, so selecting it directly would violate the intended state machine.

## Test Signals
Exercise association, multicast traffic, aggregation-heavy traffic, scan, and powersave transitions while watching RX drops, latency, and power behavior. Firmware command tracing should confirm expected `iwl_sf_cfg_cmd` values for BSS and default profiles.
