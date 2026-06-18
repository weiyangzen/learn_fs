<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/probes/decode.c -->
# sources/distributed-fs/ceph-client/arch/arm/probes/decode.c

Purpose: implements the common ARM probes instruction decoder used by kprobes and related probe users. It initializes architecture-dependent PC-write behavior, provides condition-code predicates, prepares executable instruction slots, validates encoded register operands, runs optional checker tables, and dispatches matched decode-table entries to action handlers or custom decoders.

Important APIs and functions: `arm_probes_decode_init()` runs `find_str_pc_offset()`, `test_load_write_pc_interworking()`, and `test_alu_write_pc_interworking()`. `probes_condition_checks[16]` maps ARM condition fields to CPSR tests. `probes_simulate_nop()` and `probes_emulate_none()` are generic handlers. `probes_decode_insn()` is the central table interpreter. Internally, `prepare_emulated_insn()`, `set_emulated_insn()`, `decode_regs()`, and `run_checkers()` implement slot preparation, instruction rewriting, register legality checks, and checker invocation.

Control flow: `probes_decode_insn()` initializes `asi->stack_space` to 0 and `asi->register_usage_flags` to all bits set, optionally prepares an emulation slot, then walks a packed table of `decode_*` structures. A matching table entry first passes `decode_regs()`. Table entries can jump into subtables, invoke custom decoders, assign simulate handlers, assign emulate handlers plus slot contents, combine matches with `DECODE_OR`, or reject. Checkers run on the original instruction before action dispatch.

State and persistence: persistent boot-time state is limited to `str_pc_offset`, `load_write_pc_interworks`, and `alu_write_pc_interworks` on architectures where compile-time constants are not sufficient. Per-instruction decode state is written into `struct arch_probes_insn`: handler pointers, copied instruction slot, stack usage, and register usage flags.

Dependencies and integration: depends on `decode.h`, ARM CPSR bit definitions, opcode conversion helpers, and checker/action arrays supplied by ARM or Thumb kprobe code. It is called from `arch_prepare_kprobe()` through ISA-specific wrappers such as `arm_probes_decode_insn()` and Thumb decode functions.

Risks: register rewriting is tightly coupled to handler assembly register conventions (`INSN_NEW_BITS` maps fields to r0-r3/r2/r0/r1 layouts). Incorrect condition checks or PC interworking detection can silently alter control flow. Checker failures only reject when returning `INSN_REJECTED`; missing checker coverage leaves conservative all-register usage but may miss stack hazards if action tables are incomplete.

Test signals: `test-core.c` validates decode-table consistency and coverage, while `test-arm.c` and `test-thumb.c` exercise legal and rejected register encodings, PC writes, conditional execution, and stack-sensitive stores.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/probes/decode.c -->
