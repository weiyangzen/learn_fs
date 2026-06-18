# sources/distributed-fs/ceph-client/arch/arc/kernel/unaligned.h

Purpose: declares or stubs the ARC unaligned access emulation entry point.

Important APIs/types/functions: forward-declares `struct pt_regs` and `struct callee_regs`; declares `misaligned_fixup()` when `CONFIG_ARC_EMUL_UNALIGNED` is enabled; otherwise provides an inline implementation returning `1` to indicate the fault was not fixed.

Control flow: callers can unconditionally call `misaligned_fixup()` and branch on a nonzero failure result. The header collapses the disabled configuration to a compile-time no-fixup path.

State and persistence: no state.

Dependencies and integration: included by trap handling and implemented by `unaligned.c`. Its return convention is part of `do_misaligned_access()` behavior.

Risks: any change to return semantics must be coordinated with `traps.c`, where nonzero means deliver normal misaligned error handling. Forward declarations must stay consistent with ARC register structures.

Test signals: build coverage with `CONFIG_ARC_EMUL_UNALIGNED=y` and `n`, plus misaligned access tests that verify the disabled path signals rather than emulates.
