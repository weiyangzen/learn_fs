
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/tda10071_priv.h

## Purpose
`tda10071_priv.h` contains private state, MODCOD mapping, register-mask helper structures, firmware filename, command IDs, and command-buffer layout for the TDA10071 implementation.

## Important APIs, Types, and Functions
`struct tda10071_dev` is the driver state: frontend, I2C client, regmap, command mutex, platform settings, measurement counters, cached frontend status, delivery system, warm flag, and cumulative DVBv5 error counters. `TDA10071_MODCOD[]` maps delivery/modulation/FEC combinations to firmware mode bytes. `struct tda10071_reg_val_mask` supports masked register scripts. `struct tda10071_cmd` holds up to `TDA10071_ARGLEN` command bytes. Macros define `TDA10071_FIRMWARE` and all firmware command IDs.

## Control Flow
The header has no standalone flow. `tda10071.c` uses the MODCOD table during tune validation, uses command IDs for firmware RPCs, and uses the state fields across probe/init/tune/status/sleep.

## State and Persistence Behavior
It declares volatile runtime state only. `warm` records firmware-running state, `meas_count` suppresses repeated metric updates, and `post_bit_error`/`block_error` accumulate software counters over time.

## Dependencies and Integration Points
It includes DVB frontend, public `tda10071.h`, firmware, and regmap interfaces. It is private to `tda10071.c`.

## Risks and Edge Cases
`TDA10071_MODCOD` defines the accepted tuning matrix; unsupported but theoretically valid combinations will be rejected. `TDA10071_ARGLEN` must cover every command sequence; adding longer firmware commands requires changing this bound. The table is not `const`, so accidental writes would alter tune validation globally.

## Test Signals
Tests should cover all MODCOD entries, command buffer lengths for each firmware command, metric counter accumulation, and initialization paths that transition `warm` from false to true.
