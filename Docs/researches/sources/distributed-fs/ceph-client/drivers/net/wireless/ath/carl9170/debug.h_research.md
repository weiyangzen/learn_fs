# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/carl9170/debug.h

## Purpose

`debug.h` defines the register lists, statistics storage, debug ring, and public debugfs lifecycle prototypes used by `debug.c`. It is the compile-time bridge between the carl9170 debugfs implementation and the shared AR9170 register maps.

## Important APIs, Types, and Functions

`struct hw_stat_reg_entry` maps a register address to a printable register name. `hw_rx_tally_regs`, `hw_phy_errors_regs`, `hw_tx_tally_regs`, `hw_wlan_queue_regs`, `hw_ampdu_info_regs`, and `hw_pta_queue_regs` define the exact hardware counters/registers exposed through debugfs. `struct ath_stats` stores per-register counters and cumulative tally sums. `struct carl9170_debug_mem_rbe` and `CARL9170_DEBUG_RING_SIZE` define the register-read ring. `struct carl9170_debug` embeds all debug state in `struct ar9170`.

## Control Flow

The header has no runtime flow of its own. Its arrays are consumed by the generated debugfs read helpers in `debug.c`: register addresses are copied into command lists, read by `carl9170_read_mreg()`, stored in `ar->debug.stats`, and formatted for userspace. The ring fields are used by write-triggered register reads and the paired read callback.

## State and Persistence Behavior

All state defined here is per-device debug state. Tally sums persist for the device lifetime or until the device state is reset by higher-level lifecycle code. The register-read ring persists between a debugfs write that queues reads and the following debugfs read that drains results.

## Dependencies and Integration Points

The register arrays depend on definitions from `eeprom.h`, `wlan.h`, `hw.h`, `fwdesc.h`, `fwcmd.h`, and the shared ath regulatory header. The header is included by the core carl9170 debug code and must match the names expected by `debug.c`'s macros.

## Risks and Edge Cases

Changing any register array affects the size of corresponding `ath_stats` arrays and debugfs output. Because `nreg` is fixed at 32 bytes, long macro names would truncate if introduced. The debug ring lock is declared here but current debugfs draining relies mainly on the outer device mutex and ring indexes; future parallel access should verify locking.

## Test Signals

Compile with debugfs enabled and disabled. Verify `ARRAY_SIZE()`-derived storage matches every register list. Read the hardware tally and register debugfs files and confirm the displayed names match the intended MAC/PTA register constants.
