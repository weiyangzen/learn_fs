# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/carl9170/cmd.c

## Purpose
`cmd.c` implements basic carl9170 firmware command helpers: register read/write, echo testing, command buffer allocation, reboot/reset, beacon control, tally collection, and firmware power-save commands.

## Important APIs, types, and functions
`carl9170_write_reg()` sends `CARL9170_CMD_WREG`. `carl9170_read_mreg()` and `carl9170_read_reg()` send `CARL9170_CMD_RREG` and convert little-endian responses. `carl9170_echo_test()` validates command roundtrip. `carl9170_cmd_buf()` allocates a `struct carl9170_cmd` and initializes header fields. `carl9170_reboot()` sends async reboot, `carl9170_mac_reset()` sends software reset, `carl9170_bcn_ctrl()` sends async beacon control, `carl9170_collect_tally()` updates driver and survey counters from firmware, and `carl9170_powersave()` sends async PSM state.

## Control flow and integration
Most helpers package little-endian payloads and call `carl9170_exec_cmd()` synchronously or `__carl9170_exec_cmd(..., true)` for allocated async command buffers. Error paths rate-limit logging for register access. Tally collection divides firmware active/CCA/TX times by firmware tick, accumulates counters, and updates the current channel's `survey_info` in milliseconds using `do_div`.

## State and persistence behavior
Register helpers do not keep state locally, but they mutate device registers through firmware. `carl9170_collect_tally()` persists cumulative values in `ar->tally` and current-channel `ar->survey[]`. `carl9170_powersave()` changes firmware PSM state. Command buffers are short-lived and freed by the lower execution path when requested.

## Dependencies
The file depends on `carl9170.h`, `cmd.h`, firmware command IDs and payload structs, USB command execution, mac80211 survey structures, endian conversion, and `net_ratelimit()` diagnostics.

## Risks
Risks include abusing the output buffer as the register-offset input buffer in `carl9170_read_mreg()` when callers provide overlapping or undersized storage, endian mistakes, command execution after device teardown, incorrect tally unit conversion, and async command allocation failures. The register-write batching macros in `cmd.h` rely on these primitives.

## Test signals
Signals include echo test success, single and multi-register read/write readback, software reset/reboot behavior, beacon control effects, survey/tally updates under traffic, powersave transitions around beacons, and command timeout/restart handling.
