<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/align.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/align.c

Purpose: Handles PowerPC alignment exceptions by emulating selected unaligned user accesses, SPE loads/stores, and DCBZ where safe.

Important APIs/types/functions: `struct aligninfo`, SPE decode table, `emulate_spe()` under `CONFIG_SPE`, and exported `fix_alignment(struct pt_regs *regs)`.

Control flow: `fix_alignment()` fetches the faulting instruction from kernel or user memory, swaps it for old little-endian modes if needed, special-cases SPE opcodes, rejects copy/paste and atomic LARX/STCX cases, analyzes the instruction, emulates DCBZ or load/store, and returns success, fault, or SIGBUS-driving errors.

State and persistence: Mutates the interrupted task register state, SPE EVR state, and/or user memory when emulation succeeds. Uses current thread SPE state after flushing live registers.

Dependencies and integration points: Depends on instruction analysis/emulation helpers, user access primitives, CPU feature checks, SPE support, emulated operation warnings, and `pt_regs` fault fields.

Risks: User access fault handling must be exact. Emulating unsupported atomic or copy/paste instructions would violate architecture semantics. Endian handling and SPE register pairing are subtle.

Test signals: Alignment exception selftests for loads/stores/DCBZ, SPE unaligned access tests, bad-address `-EFAULT` paths, copy/paste SIGBUS behavior, and kernel/user instruction-fetch cases.

Source read size: 355 lines, 8473 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/align.c -->
