# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnx2x/bnx2x_self_test.c

## Purpose

`bnx2x_self_test.c` implements the Broadcom `bnx2x` driver's hardware idle-check diagnostic. Its public entry point, `bnx2x_idle_chk(struct bnx2x *bp)`, walks a large static register-test database and reports hardware blocks that are not in their expected idle/error-free state. The checks cover PCIe/PXP/PGLUE, DMAE, CFC/CDU, queue manager state, parser/SDM/CM/SEM blocks, BRB/DORQ/NIG/IGU/PBF credits and FIFOs, interrupt status, parity status, SR-IOV/FLR request state, and chip-generation-specific register layouts.

This file is not the main ethtool self-test implementation despite its name. It is compiled into `bnx2x.o` and declared in `bnx2x.h`, but the direct in-tree call site found in this source set is the crash/panic diagnostic path in `bnx2x_main.c`, which runs the idle check twice after firmware dump when the device is a PF. The ethtool self-test path in `bnx2x_ethtool.c` performs NVRAM/register/memory/loopback/interrupt tests separately.

## Important APIs, Types, and Functions

- `int bnx2x_idle_chk(struct bnx2x *bp)`: exported within the driver via the prototype in `bnx2x.h`; initializes per-run counters and chip-type globals, scans `st_database`, reads MMIO registers, evaluates predicates, logs failures, and returns the number of hard idle-check errors.
- `struct st_record`: one row of the generated self-test database. Fields include `chip_mask`, `macro`, `reg1`, `reg2`, loop count/increment, predicate function pointer, optional `reg3`, severity, failure message, and predicate immediates.
- `struct st_pred_args`: transient predicate argument bundle containing read values (`val1`, `val2`) and up to four immediate constants.
- `st_database[468]`: generated register-test table. The comments preserve original CSV line numbers 2 through 469. Each row selects applicable chips, register access pattern, predicate, severity, and diagnostic string.
- Predicate helpers: `peq`, `pneq`, `pand_neq`, `pand_neq_x2`, `pneq_err`, `pgt`, `pneq_r2`, `plt_sub_r2`, `pne_sub_r2`, `prsh_and_neq`, `peq_neq_r2`, and `peq_neq_neq_r2`. They encode simple comparisons, masked comparisons, shifted-field checks, and two-register relationships.
- `bnx2x_self_test_log()`: central severity handler. `IDLE_CHK_ERROR` emits `BNX2X_ERR()` and increments `idle_chk_errors`; `IDLE_CHK_WARNING` emits `DP(NETIF_MSG_HW, ...)` and increments `idle_chk_warnings`; `IDLE_CHK_ERROR_NO_TRAFFIC` is logged as informational hardware debug and does not increment the error counter.
- `bnx2x_idle_chk6()`: special queue-manager pointer-table check. It extracts read/write pointers and banks from paired words and logs mismatches per table entry.
- `bnx2x_idle_chk7()`: special CFC info-RAM/CID-CAM check. It skips invalid CAM entries, performs required wide-bus reads, extracts connection type using E1/E1H vs E2/E3 bit positions, reads activity counters, and applies the row predicate.

## Control Flow

`bnx2x_idle_chk()` starts by resetting the file-scope counters `idle_chk_errors` and `idle_chk_warnings`, then caches chip-generation booleans using `CHIP_IS_E1()`, `CHIP_IS_E1H()`, `CHIP_IS_E2()`, `CHIP_IS_E3A0()`, and `CHIP_IS_E3B0()`.

The main loop copies each `st_database` row into a local `struct st_record rec` and skips rows whose `chip_mask` does not match the current chip. Matching rows dispatch on `rec.macro`:

- Macro `1`: read one register and evaluate the predicate once.
- Macro `2`: read a register range from `reg1 + i * incr` for `loop` iterations.
- Macro `3`: read `reg1` and `reg2`, then evaluate a two-value predicate.
- Macro `4`: currently marked unused, but implemented as a loop over two registers where the second read is shifted right one bit.
- Macro `5`: read `reg1` and `reg2`, but evaluate only when condition register `reg3` is nonzero.
- Macro `6`: delegate to `bnx2x_idle_chk6()` for QM pointer/bank consistency.
- Macro `7`: delegate to `bnx2x_idle_chk7()` for CFC connection-type/activity-counter consistency.

When a predicate reports failure, the function formats a bounded message with `snprintf(message, sizeof(message), ...)` or `MAX_FAIL_MSG` and sends it through `bnx2x_self_test_log()`. After all rows are scanned, the function returns immediately with the error count if `netif_running(bp->dev)` is false. If the interface is running, it emits a success/failure summary and still returns `idle_chk_errors`.

## State and Persistence Behavior

The file keeps run-local statistics and chip booleans in file-scope statics: `idle_chk_errors`, `idle_chk_warnings`, `is_e1`, `is_e1h`, `is_e2`, `is_e3a0`, and `is_e3b0`. `bnx2x_idle_chk()` overwrites all of them at the start of each run, so they are not persistent across deliberate invocations, but they are shared mutable state inside the module.

`st_database` is static and initialized at compile time. The code copies each row before use, which means runtime writes to `rec.pred_args.val1` and `val2` do not mutate the database rows. The register reads are side-effect-sensitive MMIO reads via `REG_RD()`; some wide-bus accesses in `bnx2x_idle_chk7()` intentionally perform throwaway reads before taking the relevant word.

No disk state, firmware state, NVRAM, or kernel configuration is persisted by this file. Observable side effects are kernel logs/debug messages and MMIO reads from device register space.

## Dependencies and Integration Points

- Includes `<linux/kernel.h>`, `<linux/netdevice.h>`, and `bnx2x.h`.
- Depends on `struct bnx2x` fields including `bp->dev`, `bp->regview`, and `bp->msg_enable` through logging and MMIO macros.
- Uses `REG_RD(bp, offset)`, which maps to `readl(REG_ADDR(bp, offset))` in `bnx2x.h`.
- Uses `BNX2X_ERR()` for unmasked error logs and `DP()` with `NETIF_MSG_HW` or `BNX2X_MSG_IDLE` masks for debug logs.
- Uses Linux networking state via `netif_running()`.
- Uses hundreds of register constants from the `bnx2x` register/header set, including `PXP2_REG_*`, `PGLUE_B_REG_*`, `QM_REG_*`, `CFC_REG_*`, `NIG_REG_*`, `IGU_REG_*`, `MISC_REG_*`, and many block-specific status/credit/parity registers.
- Integrated into the build through `drivers/net/ethernet/broadcom/bnx2x/Makefile` as `bnx2x_self_test.o`.
- Called from the PF crash dump path in `bnx2x_main.c` after `bnx2x_fw_dump()`, with `NETIF_MSG_HW` temporarily enabled so warning/info diagnostics become visible.

## Risks and Edge Cases

- The file-scope counters and chip booleans make `bnx2x_idle_chk()` non-reentrant. Concurrent invocations for different devices would race and could produce mixed counts or wrong chip-specific behavior in `bnx2x_idle_chk7()`.
- The database is hand/generated table logic tied tightly to chip revisions and register layouts. Incorrect `chip_mask`, register constants, predicate immediates, or severity values can silently misclassify hardware state.
- `NA` is defined as `0xCD` and reused in integer fields where a value is "not applicable". If a macro path accidentally consumes an `NA` field as a loop count, increment, register address, or predicate immediate, it can perform unintended reads or comparisons. Current macro dispatch mostly avoids those fields by convention rather than type safety.
- `IDLE_CHK_ERROR_NO_TRAFFIC` intentionally does not increment `idle_chk_errors`; callers relying only on the return value will not see no-traffic idle violations as failures.
- `pneq_err()` depends on the current cumulative `idle_chk_errors` count, so its result depends on prior table rows and their severities. Reordering database records can change whether those warnings fire.
- The function performs many MMIO reads and may be expensive/noisy during error recovery or crash handling. The crash path calls it twice, which can help distinguish transient state but doubles register-read volume.
- The summary logging is skipped when the netdevice is down, but the database scan has already happened. A down interface still sees register reads and per-row error logging before the final early return.
- Diagnostic strings contain a few typos and inconsistent wording inherited from the generated table; downstream log parsers should key off block/register context rather than exact prose when possible.

## Test Signals

Useful validation signals for this file are mostly compile-time and hardware/diagnostic behavior:

- Build with `CONFIG_BNX2X=y` or `m` to verify `bnx2x_self_test.o` links and the `bnx2x_idle_chk()` prototype remains consistent with `bnx2x.h`.
- Static checks should ensure all `st_record` predicate pointers are non-null, all macro values are handled or intentionally logged as unknown, and `ST_DB_LINES` matches the number of table entries.
- A crash-dump or controlled diagnostic run on supported hardware should show `Idle check (1st round)` and `Idle check (2nd round)` from `bnx2x_main.c`, followed by either `completed successfully` with warning count or `failed` with error/warning counts.
- Hardware test expectations should include separate interpretation of warnings, hard errors, and `IDLE_CHK_ERROR_NO_TRAFFIC` informational idle violations because only hard errors affect the return value.
- Regression tests around this file should focus on database row changes: applicable chip mask, macro type, register offsets, predicate/immediate semantics, severity, and whether a changed row should affect `idle_chk_errors`.
