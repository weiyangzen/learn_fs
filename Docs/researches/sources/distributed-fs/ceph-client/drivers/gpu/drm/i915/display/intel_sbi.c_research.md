<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_sbi.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_sbi.c

## Purpose
`intel_sbi.c` implements locked access to the LPT/WPT IOSF Sideband Interface used by display code to program ICLK and MPHY sideband registers, especially for PCH refclock/SSC setup.

## Important APIs, Types, And Functions
The central helper is `intel_sbi_rw()`, which performs one read or write transaction. Public functions are `intel_sbi_init()`, `intel_sbi_fini()`, `intel_sbi_lock()`, `intel_sbi_unlock()`, `intel_sbi_read()`, and `intel_sbi_write()`. The destination enum is declared in `intel_sbi.h`.

## Control Flow
Callers are expected to acquire `display->sbi.lock` with `intel_sbi_lock()`. `intel_sbi_rw()` waits up to 100 ms for `SBI_CTL_STAT` to report ready, writes `SBI_ADDR`, writes `SBI_DATA` for writes, composes a command for ICLK or MPHY and read/write operation, marks the transaction busy, waits for completion, checks `SBI_RESPONSE_FAIL`, and reads back `SBI_DATA` for reads. Public read/write wrappers ignore the internal error code except that reads return 0 on failure.

## State And Persistence Behavior
The only software state is `display->sbi.lock`, initialized and destroyed by the init/fini functions. Hardware state is whatever sideband registers callers modify. Lockdep asserts that transactions occur with the mutex held.

## Dependencies And Integration Points
The file uses `intel_de_*_fw` MMIO helpers, DRM logging, display core state, and register definitions from `intel_sbi_regs.h`. It is initialized from driver setup/teardown and used heavily by `intel_pch_refclk.c`.

## Risks
The wrapper read/write APIs do not propagate transaction errors, so callers may proceed with a 0 read or failed write after logging. Destination-specific command selection is asymmetric: ICLK uses `SBI_CTL_OP_CRRD`, MPHY uses `SBI_CTL_OP_IORD`, and writes add `SBI_CTL_OP_WR`; any future destination or operation needs careful command encoding. Missing locks can race sideband transactions.

## Test Signals
Signals include absence of SBI timeout/error logs, correct refclock/SSC behavior on LPT/WPT systems, lockdep coverage for held locks, and successful display bring-up on platforms that require sideband programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_sbi.c -->
