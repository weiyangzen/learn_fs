# sources/distributed-fs/ceph-client/arch/x86/lib/csum-copy_64.S

Purpose: implements 64-bit checksum-copy core used by x86 networking wrappers, copying memory while computing an unfolded Internet checksum with exception recovery.

Important APIs/functions: defines `csum_partial_copy_generic`. It uses local `source` and `dest` macros to annotate faulting loads/stores with uaccess exception table entries that branch to `.Lfault`.

Control flow: saves callee registers, initializes sum to `-1`, handles destination alignment including odd-byte rotation bookkeeping, processes 64-byte chunks with eight qword loads, checksum accumulation using carry, and eight qword stores. It then handles 8-byte, 2-byte, and 1-byte tails, folds the 64-bit accumulator to 32 bits, rotates if the original alignment was odd, and restores registers. Any source or destination fault returns zero via `.Lfault`; wrappers handle higher-level validity.

State and persistence behavior: writes destination memory while reading source memory. No global state. On exceptions destination can be partially written and checksum return is zero.

Dependencies/integration points: called by `csum-wrappers_64.c` for user and kernel copy/checksum APIs. Depends on x86 exception tables, uaccess annotations, and networking checksum conventions.

Risks: checksum correctness depends on carry propagation, fold order, and odd alignment rotation. The function does not distinguish source versus destination faults to callers; wrapper contracts must tolerate zero checksum on fault. Prefetch exceptions are deliberately non-uaccess and ignored.

Test signals: checksum-copy tests for aligned/unaligned and odd source/destination cases, fault injection during source/destination access, comparison with generic checksum implementation, and network stack checksum validation.
