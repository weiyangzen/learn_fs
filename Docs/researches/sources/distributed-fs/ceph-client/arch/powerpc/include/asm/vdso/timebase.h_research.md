<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/vdso/timebase.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/vdso/timebase.h

Purpose: Defines PowerPC timebase read/write helpers used by vDSO and low-level timekeeping.

Important APIs/types/functions: `mftb()`, `mftbu()`, `mttbl()`, `mttbu()`, `get_tb()`, and `set_tb()` with special cases for Cell, e500, and 8xx.

Control flow: 64-bit vDSO reads the lower timebase directly; 32-bit-compatible code loops high-low-high until stable. Cell bug handling retries a zero lower timebase when the CPU feature is set. `set_tb()` writes upper/lower timebase registers in the required order.

State and persistence: Interacts directly with CPU timebase special-purpose registers. `get_tb()` is read-only; `set_tb()` mutates global processor timebase state and is only appropriate for kernel-side setup.

Dependencies and integration points: Depends on `asm/reg.h` for SPR numbers and feature macros. Integrated by vDSO clocks, kernel time setup, and architecture code that needs stable TB values.

Risks: A non-atomic 32-bit read without the retry loop can produce backwards time. Wrong SPR access or Cell workaround gating can break timekeeping on older platforms.

Test signals: Timebase monotonicity tests, vDSO time tests on 32-bit compat and 64-bit kernels, and platform boot coverage for Cell/e500/8xx configurations.

Source read size: 73 lines, 1933 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/vdso/timebase.h -->
