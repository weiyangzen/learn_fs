# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/psoc_timestamp_regs.h

Purpose: defines the PSOC timestamp/counter register map. The 17 macros expose control/status, low/high counter value, frequency ID, peripheral IDs, and component IDs.

Important APIs/types/functions: macro-only `mmPSOC_TIMESTAMP_*` constants from `mmPSOC_TIMESTAMP_CNTCR` at `0xC49000` to `mmPSOC_TIMESTAMP_CIDR3` at `0xC49FFC`. Functional registers are `CNTCR`, `CNTSR`, `CNTCVL`, `CNTCVU`, and `CNTFID0`.

Control flow: driver time initialization disables the counter, resets low/high count words, then enables it. Time reads combine `CNTCVU` and `CNTCVL` into a 64-bit device timestamp; equivalent Gaudi code demonstrates this pattern.

State and persistence: the counter value is persistent monotonic hardware state while enabled and is reset by explicit writes or reset sequencing. The header itself is stateless.

Dependencies and integration: included by `goya_regs.h` and used by time-synchronization, profiling, and device timestamp code. `goya_blocks.h` provides the block base when code accesses offsets relative to `CFG_BASE`.

Risks: reading high/low counter words without a latch or retry strategy can race rollover if hardware does not guarantee atomicity. Mixing absolute addresses with base-relative accesses is a common error around timestamp setup.

Test signals: counter enable/reset/read smoke tests, monotonicity checks, rollover-adjacent reads, frequency reporting via `CNTFID0`, and profiling timestamp correlation with host time.
