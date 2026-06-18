<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/probes/kprobes/actions-thumb.c -->
# sources/distributed-fs/ceph-client/arch/arm/probes/kprobes/actions-thumb.c

Purpose: supplies Thumb-2 kprobe action handlers for both 16-bit Thumb (T16) and 32-bit Thumb (T32) instructions and publishes the `kprobes_t16_actions` and `kprobes_t32_actions` dispatch tables.

Important functions: T32 simulation covers table branches, MRS, conditional/unconditional branches, and literal loads. T32 emulation handlers cover LDM/STM, LDRD/STRD, LDR/STR, data processing, PC-relative add/sub, bitfield, media, reverse, multiply, and long multiply forms. T16 simulation covers BX/BLX, literals, SP-relative loads/stores, ADR, SP add/sub, CBZ/CBNZ, IT, conditional/unconditional branches. T16 emulation covers low-register operations, high-register operations, push, and pop with or without PC.

Control flow: custom decoders such as `t32_decode_cond_branch()`, `t16_decode_it()`, `t16_decode_hiregs()`, `t16_decode_push()`, and `t16_decode_pop()` install specialized handlers or prepare replacement Thumb instructions. Most emulation handlers load relevant `pt_regs` values into r0-r3/r1-r2 conventions, call `asi->insn_fn`, then copy results and APSR flags back. Branch simulators compute signed Thumb offsets and set LR/interworking bits for BL/BLX.

State and persistence: no persistent global state. Runtime state is in `pt_regs`, CPSR IT bits, `asi->insn` halfwords, and selected handler pointers.

Dependencies and integration: depends on `decode-thumb.h`, `core.h`, `checkers.h`, condition checks from `decode.c`, and shared LDM/STM decode from `actions-common.c`. `core.c` selects these tables when `CONFIG_THUMB2_KERNEL` is enabled.

Risks: Thumb instruction width, halfword ordering, IT-state advancement, PC alignment (`pc & ~3`), and interworking are subtle. Push/pop emulation uses fixed scratch registers and stack conventions; clobber mistakes can corrupt saved state.

Test signals: `test-thumb.c` covers T16/T32 data processing, IT blocks, branches, table branches, literals, load/store, push/pop, interworking, hints, rejected system/exclusive/coprocessor instructions, and PC/SP illegal encodings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/probes/kprobes/actions-thumb.c -->
