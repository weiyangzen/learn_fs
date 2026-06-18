# subset-b-000666 Research

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/probes/decode.h -->
# sources/distributed-fs/ceph-client/arch/arm/probes/decode.h

Purpose: declares the shared decode-table ABI for ARM probes and defines inline helpers for PC writes, interworking, writeback detection, decode entry construction, checker/action types, and instruction decode result codes.

Important APIs and types: exports `arm_probes_decode_init()`, `probes_condition_checks`, `probes_simulate_nop`, `probes_emulate_none`, and `probes_decode_insn()`. Core types include `enum decode_type`, `enum decode_reg_type`, `union decode_item`, `union decode_action`, `struct decode_header`, `struct decode_table`, `struct decode_custom`, `struct decode_simulate`, `struct decode_emulate`, `struct decode_or`, `struct decode_reject`, and `struct decode_checker`. The `REGS()` macro encodes five register-field policies into table metadata.

Control flow: table users build arrays of `union decode_item` with macros such as `DECODE_TABLE`, `DECODE_CUSTOM`, `DECODE_SIMULATEX`, `DECODE_EMULATEX`, `DECODE_OR`, `DECODE_REJECT`, and `DECODE_END`. The runtime decoder consumes those arrays and interprets each header by type. `bx_write_pc()`, `load_write_pc()`, and `alu_write_pc()` centralize ARM/Thumb interworking semantics after simulated or emulated instructions write PC.

State and persistence: the header chooses compile-time constants for `str_pc_offset`, `load_write_pc_interworks`, and `alu_write_pc_interworks` when the configured architecture makes them invariant, otherwise it declares runtime variables and init probes in `decode.c`.

Dependencies and integration: includes Linux type definitions, `asm/probes.h`, `asm/ptrace.h`, and `asm/kprobes.h`. Decode tables in `decode-arm.h` and `decode-thumb.h`, kprobe actions, and checker modules all depend on these definitions.

Risks: table layout is binary-encoded through macros and struct size assumptions; adding a decode type requires updating size tables in both `decode.c` and `test-core.c`. Register policy aliases `NOPCX` and `NOSPPCX` exist partly for coverage semantics, so collapsing them can reduce test precision. PC-write helper behavior varies by architecture and must match ARM ARM interworking rules.

Test signals: table consistency and coverage tests inspect these structures directly. Supported/rejected instruction cases verify that `REG_TYPE_*` policies reject SP/PC/writeback combinations as intended.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/probes/decode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/probes/kprobes/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm/probes/kprobes/Makefile

Purpose: selects ARM kprobe objects for normal, Thumb-2, optimized-probe, and self-test builds.

Important build entries: disables KASAN instrumentation for `actions-common.o`, `actions-arm.o`, and `actions-thumb.o`, which is important because these files contain low-level probe emulation paths and inline assembly that run in exception-sensitive contexts. `obj-$(CONFIG_KPROBES)` always includes `core.o`, `actions-common.o`, and `checkers-common.o`. `obj-$(CONFIG_ARM_KPROBES_TEST)` builds `test-kprobes.o` from `test-core.o` plus the ISA-specific test file.

Control flow: build selection branches on `CONFIG_THUMB2_KERNEL`. Thumb-2 kernels compile `actions-thumb.o`, `checkers-thumb.o`, and `test-thumb.o`. Non-Thumb2 ARM kernels compile `actions-arm.o`, `checkers-arm.o`, optional `opt-arm.o` under `CONFIG_OPTPROBES`, and `test-arm.o`.

State and persistence: no runtime state; this file determines which object files and test cases are linked into the kernel or module.

Dependencies and integration: integrates with Kbuild and architecture Kconfig symbols. The object split mirrors runtime dispatch in `core.c`, where Thumb-2 selects T16/T32 decode/action/checker arrays and non-Thumb ARM selects ARM arrays and optimized kprobe support.

Risks: an incorrect `CONFIG_THUMB2_KERNEL` branch would compile action/checker arrays incompatible with the instruction set used by `arch_prepare_kprobe()`. Enabling KASAN here could perturb register/stack assumptions in probe handlers.

Test signals: `CONFIG_ARM_KPROBES_TEST` links either `test-arm.o` or `test-thumb.o`; successful build and boot/module test execution indicate correct object selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/probes/kprobes/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/probes/kprobes/actions-arm.c -->
# sources/distributed-fs/ceph-client/arch/arm/probes/kprobes/actions-arm.c

Purpose: provides ARM-mode kprobe action handlers and the `kprobes_arm_actions` dispatch table used by the common decoder to simulate or emulate supported ARM instructions.

Important functions: `emulate_ldrdstrd()`, `emulate_ldr()`, and `emulate_str()` handle extra and normal load/store forms with PC/SP/writeback fixups. `emulate_rd12rn16rm0rs8_rwflags()`, `emulate_rd12rn16rm0_rwflags_nopc()`, `emulate_rd16rn12rm0rs8_rwflags_nopc()`, `emulate_rd12rm0_noflags_nopc()`, and `emulate_rdlo12rdhi16rn0rm8_rwflags_nopc()` implement common register shuffles around an executable slot. `kprobes_arm_actions[]` maps `PROBES_*` action IDs to these handlers or shared simulators.

Control flow: each handler copies original registers into fixed ABI registers expected by rewritten slot instructions, calls `asi->insn_fn` via `BLX`, then writes results and APSR flags back into `pt_regs`. Loads to PC use `load_write_pc()`, ALU writes use `alu_write_pc()`, and stores from PC use `str_pc_offset`.

State and persistence: no global mutable state. It mutates trapped task register state (`struct pt_regs`) and uses `asi->insn_fn` and prepared instruction slots created during decode.

Dependencies and integration: includes `decode-arm.h`, `core.h`, and `checkers.h`. Exports `kprobes_arm_actions` and `kprobes_arm_checkers`, consumed by `arch_prepare_kprobe()` for non-Thumb2 kernels. It relies on shared simulators such as `simulate_blx1`, `simulate_mrs`, `simulate_bbl`, and `simulate_mov_ipsp` from ARM probe decode infrastructure.

Risks: inline assembly clobber lists and register constraints must match rewritten instruction operands. PC alignment/interworking differences across ARM versions are high risk. Incorrect writeback handling can corrupt base registers or stack.

Test signals: `test-arm.c` exercises each action class across condition codes, PC/SP operands, writeback addressing, ALU flags, multiply/media operations, branches, and supported/rejected encodings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/probes/kprobes/actions-arm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/probes/kprobes/actions-common.c -->
# sources/distributed-fs/ceph-client/arch/arm/probes/kprobes/actions-common.c

Purpose: implements common ARM/Thumb kprobe action logic for block data transfer instructions, especially LDM/STM forms that can be emulated through rewritten slots or simulated in software.

Important functions: `simulate_ldm1stm1()` interprets load/store multiple register lists, addressing modes, and writeback. `simulate_stm1_pc()` handles STM with PC in the register list using `str_pc_offset`. `simulate_ldm1_pc()` runs LDM then applies `load_write_pc()` for PC loads. `emulate_generic_r0_12_noflags()`, `emulate_generic_r2_14_noflags()`, and `emulate_ldm_r3_15()` provide fast slot execution for register ranges. `kprobe_decode_ldmstm()` chooses the best path and writes a modified instruction when possible.

Control flow: `kprobe_decode_ldmstm()` inspects the base register, register list, and load/store bit. If all operands fit one of the supported contiguous register windows, it rewrites the instruction and returns `INSN_GOOD` with an emulation handler. Otherwise it falls back to simulation, selecting special PC-aware handlers when the register list includes R15.

State and persistence: no global state. The decoder writes `asi->insn[0]` and `asi->insn_handler`; runtime handlers mutate memory, `pt_regs`, PC, and optional base-register writeback.

Dependencies and integration: included by both ARM and Thumb action paths through `core.h`; Thumb32 wraps `kprobe_decode_ldmstm()` to reorder halfwords after ARM-style rewriting.

Risks: LDM/STM addressing uses pre/post and up/down bits; off-by-one address adjustment would corrupt register restore or stack behavior. Fast emulation depends on legal register windows and must not include unsupported SP/PC combinations except where the dedicated PC load handler applies.

Test signals: ARM and Thumb test catalogs include many LDM/STM variants, stack forms, PC-loading branches, and register-list combinations, while stack checkers constrain dangerous SP stores.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/probes/kprobes/actions-common.c -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/probes/kprobes/checkers-arm.c -->
# sources/distributed-fs/ceph-client/arch/arm/probes/kprobes/checkers-arm.c

Purpose: provides ARM-mode decode checkers for stack usage and register usage metadata. These checkers run during instruction preparation after a decode-table action has matched.

Important functions: `arm_check_stack()` uses a nested decode table to classify stack effects for stores and LDM/STM. It maps normal instructions to `STACK_USE_NONE`, register-indexed stores using SP to `STACK_USE_UNKNOWN`, decrementing SP stores to fixed byte counts, and STMDX forms to register-list-derived stack usage. Register checkers include `arm_check_regs_nouse()`, `arm_check_regs_normal()`, `arm_check_regs_ldmstm()`, `arm_check_regs_mov_ip_sp()`, and `arm_check_regs_ldrdstrd()`.

Control flow: `kprobes_arm_checkers[]` chains `arm_stack_checker` and `arm_regs_checker`. The common decoder passes the matched action index into both arrays. Stack checkers may recursively call `probes_decode_insn()` on the original instruction with `stack_check_actions`; register checkers set `asi->register_usage_flags` directly from register fields, register lists, or known special cases.

State and persistence: no global state. It writes `asi->stack_space` and `asi->register_usage_flags`, which later affect `arch_prepare_kprobe()` rejection and optimized-probe direct execution decisions.

Dependencies and integration: depends on `decode.h`, `decode-arm.h`, and `checkers.h`. Integrated only for non-Thumb2 builds through `actions-arm.c` and `core.h`.

Risks: underestimated stack usage can allow probes on instructions that overwrite the kprobe exception stack frame; overestimated or unknown usage rejects valid probes or disables optimization. Register usage flags drive optprobe direct execution, so missing implicit registers such as `Rt+1` for LDRD/STRD would be unsafe.

Test signals: ARM tests include SP-relative negative stores at `MAX_STACK_SIZE`, unknown register-indexed SP stores, LDM/STM stack cases, LDRD/STRD implicit register pairs, and optprobe benchmarks that benefit from accurate register usage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/probes/kprobes/checkers-arm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/probes/kprobes/checkers-common.c -->
# sources/distributed-fs/ceph-client/arch/arm/probes/kprobes/checkers-common.c

Purpose: implements shared checker action decoders that classify stack space usage for ARM and Thumb kprobe safety checks.

Important functions: `checker_stack_use_none()` sets stack usage to 0. `checker_stack_use_unknown()` sets it to -1. Immediate helpers compute stack byte counts from instruction encodings: `checker_stack_use_imm_0xx()` for Thumb imm8, `checker_stack_use_t32strd()` for Thumb32 STRD imm8 scaled by 4, `checker_stack_use_imm_x0x()` for ARM split halfword immediates when Thumb2 is not configured, and `checker_stack_use_imm_xxx()` for ARM imm12. `checker_stack_use_stmdx()` derives stack cost from register-list population and pre/post indexing.

Control flow: architecture-specific stack checkers decode a suspicious store form to one of the `STACK_USE_*` action IDs; `stack_check_actions[]` maps that ID to these functions. The functions return `INSN_GOOD_NO_SLOT` because no executable instruction slot is needed for metadata-only classification.

State and persistence: no persistent state. It writes `asi->stack_space`, where negative means statically unknown and positive means extra bytes of stack below SP that must be protected.

Dependencies and integration: depends on `decode.h`, ARM decode definitions, and `checkers.h`; selected helper availability is conditional on `CONFIG_THUMB2_KERNEL`.

Risks: immediate extraction differs across ARM, T16, and T32 encodings. A wrong scale for STRD or incorrect STMDB pre/post adjustment changes whether `arch_prepare_kprobe()` accepts unsafe stack stores. Returning metadata-only success must not be confused with an executable action.

Test signals: both ARM and Thumb tests include fixed negative SP stores at and beyond `MAX_STACK_SIZE`, register-indexed SP stores expected to be rejected as unknown, and push/STMDB forms whose stack byte count is register-list dependent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/probes/kprobes/checkers-common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/probes/kprobes/checkers-thumb.c -->
# sources/distributed-fs/ceph-client/arch/arm/probes/kprobes/checkers-thumb.c

Purpose: provides Thumb-specific stack checkers for T32 load/store families and T16 push instructions.

Important functions: `t32_check_stack()` contains a nested decode table that first ignores all loads, marks register-indexed stores involving SP as unknown, computes fixed stack use for negative SP immediate stores, handles T32 STRD scaling, handles STMDB register-list stack use, and defaults to no stack use. `t16_check_stack()` computes push stack space as `hweight32(reglist) * 4`.

Control flow: `t32_stack_checker[]` attaches `t32_check_stack()` to T32 LDM/STM, LDRD/STRD, and LDR/STR actions. `t16_stack_checker[]` attaches `t16_check_stack()` only to `PROBES_T16_PUSH`, reflecting that other 16-bit Thumb stack-relevant stores cannot address below SP in the same dangerous way.

State and persistence: no global state. Writes `asi->stack_space`, which `arch_prepare_kprobe()` later bounds against `MAX_STACK_SIZE`.

Dependencies and integration: depends on `decode-thumb.h`, shared `stack_check_actions`, and `checkers.h`. Used only in Thumb2 kernels through `kprobes_t32_checkers` and `kprobes_t16_checkers`.

Risks: T32 register-store encodings include invalid patterns intentionally used to simplify masks; changes to decode tables need matching checker masks. T16 stack classification assumes only push can require extra protected stack space, so adding new T16 store actions requires reassessment.

Test signals: `test-thumb.c` includes push register lists, T32 STR/STRB/STRH/STRD negative SP stores, register-offset SP stores expected to be unsupported, and boundary cases around `MAX_STACK_SIZE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/probes/kprobes/checkers-thumb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/probes/kprobes/checkers.h -->
# sources/distributed-fs/ceph-client/arch/arm/probes/kprobes/checkers.h

Purpose: declares the checker action interface and stack-use classification IDs shared by ARM and Thumb kprobe checker implementations.

Important APIs and types: exports `checker_stack_use_none`, `checker_stack_use_unknown`, immediate stack-use helpers selected by `CONFIG_THUMB2_KERNEL`, `checker_stack_use_imm_xxx`, and `checker_stack_use_stmdx`. Defines the `STACK_USE_*` enum used as action indexes into `stack_check_actions[]`. Declares checker arrays for ARM (`arm_stack_checker`, `arm_regs_checker`) on non-Thumb2 builds and Thumb (`t32_stack_checker`, `t16_stack_checker`) generally.

Control flow: architecture-specific checker tables use action IDs from this header when their nested decode tables classify an instruction. The shared decoder treats these actions as custom decoders, so the checker function updates `struct arch_probes_insn` metadata and returns an `enum probes_insn`.

State and persistence: no state in the header. It defines how checker code writes stack/register metadata into `arch_probes_insn`.

Dependencies and integration: includes `decode.h` for `probes_check_t`, `union decode_action`, and `struct decode_checker`. Used by all `actions-*` files to expose checker arrays consumed by `core.c`.

Risks: enum ordering must stay synchronized with `stack_check_actions[]` in `checkers-common.c` and with decode-table action IDs in checker tables. Conditional enum members differ between Thumb2 and ARM builds, so cross-ISA assumptions about numeric values are unsafe.

Test signals: compile coverage across Thumb2 and non-Thumb2 builds is important because different declarations and enum members are active. Runtime tests validate the stack metadata produced through these declarations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/probes/kprobes/checkers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/probes/kprobes/core.c -->
# sources/distributed-fs/ceph-client/arch/arm/probes/kprobes/core.c

Purpose: implements ARM architecture kprobe and kretprobe lifecycle: instruction preparation, breakpoint patching, trap dispatch, single-step simulation/emulation, fault recovery, return-probe trampoline setup, undefined-instruction hook registration, and blacklist checks.

Important functions: `arch_prepare_kprobe()`, `arch_arm_kprobe()`, `arch_disarm_kprobe()`, `arch_remove_kprobe()`, `kprobes_remove_breakpoint()`, `kprobe_handler()`, `kprobe_trap_handler()`, `kprobe_fault_handler()`, `__kretprobe_trampoline()`, `arch_prepare_kretprobe()`, `arch_init_kprobes()`, and `arch_within_kprobe_blacklist()`. Per-CPU state is `current_kprobe` and `kprobe_ctlblk`.

Control flow: probe registration decodes the target instruction according to ARM/T16/T32 mode, allocates an instruction slot when needed, flushes caches, and rejects unsupported or stack-unsafe instructions. Arming patches an undefined-instruction breakpoint with ISA-appropriate encoding. Trap handling looks up the probe at PC, checks conditional execution, handles recursive hits, runs pre-handler, single-steps via the selected `ainsn` function, runs post-handler, and resets current state. Fault handling restores PC to the original probe address when emulation faults.

State and persistence: modifies kernel text via `patch_text()`/`__patch_text()`, stores prepared instruction slots in `p->ainsn`, and maintains per-CPU current-probe status. Kretprobes replace LR with `__kretprobe_trampoline` and store original return/fp in the instance.

Dependencies and integration: depends on decode/action/checker tables, undefined instruction hooks, text patching, stop_machine synchronization, instruction slot allocators, kprobe core APIs, and ARM exception sections.

Risks: breakpoint removal needs stop_machine to avoid SMP races and Thumb32 halfword tearing. IRQs remain disabled during probe handling to prevent unsupported nesting. Incorrect condition/IT skipping or PC restoration can replay or skip target instructions.

Test signals: `test-core.c` API tests verify kprobe/kretprobe registration, handler calls, unregister behavior, instruction simulation comparisons, and benchmarks. Blacklist behavior is not directly covered by the listed tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/probes/kprobes/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/probes/kprobes/core.h -->
# sources/distributed-fs/ceph-client/arch/arm/probes/kprobes/core.h

Purpose: declares ARM kprobe-private constants and cross-file interfaces for breakpoint encodings, breakpoint removal, LDM/STM decode, ISA-specific action/checker tables, and the decode-function signature used by core preparation.

Important APIs and types: defines `KPROBE_ARM_BREAKPOINT_INSTRUCTION`, `KPROBE_THUMB16_BREAKPOINT_INSTRUCTION`, and `KPROBE_THUMB32_BREAKPOINT_INSTRUCTION`. Declares `kprobes_remove_breakpoint()`, `kprobe_decode_ldmstm()`, and `typedef kprobe_decode_insn_t`. Exposes `kprobes_t32_actions`, `kprobes_t16_actions`, `kprobes_t32_checkers`, and `kprobes_t16_checkers` for Thumb2, or `kprobes_arm_actions` and `kprobes_arm_checkers` for ARM mode.

Control flow: `core.c` includes this header to select the appropriate decode/action/checker arrays in `arch_prepare_kprobe()`. `actions-common.c` exports the LDM/STM custom decoder declared here.

State and persistence: no state; the constants define the persistent breakpoint instruction values that get patched into kernel text while probes are armed.

Dependencies and integration: includes `asm/kprobes.h` and shared `decode.h`. It is the narrow coupling layer between core probe management and action/checker implementations.

Risks: breakpoint encodings must remain unique and reserved for kprobes undefined-instruction hooks. A mismatch between declarations and Makefile-selected objects will cause link failures or runtime decode table misuse. The decode-function typedef must match ARM/Thumb decode wrapper signatures.

Test signals: build and boot-time kprobe tests indirectly validate that the right arrays are linked and that breakpoint values trap through the registered undefined hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/probes/kprobes/core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/probes/kprobes/opt-arm.c -->
# sources/distributed-fs/ceph-client/arch/arm/probes/kprobes/opt-arm.c

Purpose: implements ARM-mode optimized kprobes by replacing an armed probe breakpoint with a direct branch to an out-of-line template that saves registers, calls the optimized kprobe callback, optionally executes the original instruction directly, restores state, and branches back.

Important functions: `arch_prepared_optinsn()`, `arch_check_optimized_kprobe()`, `arch_prepare_optimized_kprobe()`, `arch_optimize_kprobes()`, `arch_unoptimize_kprobe()`, `arch_unoptimize_kprobes()`, `arch_within_optimized_kprobe()`, and `arch_remove_optimized_kprobe()`. `optimized_callback()` invokes `opt_pre_handler()` and falls back to single-step when direct execution is unavailable.

Control flow: `arch_prepare_optimized_kprobe()` rejects unknown or too-large stack usage, allocates an optinsn slot, checks that the branch from original address to slot is within ARM's signed 24-bit branch range, copies the assembly template, patches stack-protection immediates, stores callback operands, and may embed the original instruction in the restore path if `register_usage_flags` shows PC is unused and a return branch can be generated. `arch_optimize_kprobes()` patches the original instruction with a conditional branch preserving the original condition code.

State and persistence: allocates and frees optimized instruction slots, stores copied original instruction bytes in `op->optinsn.copied_insn`, sets `orig->ainsn.kprobe_direct_exec`, and patches live kernel text.

Dependencies and integration: depends on ARM branch generation, cache flushing, text patching, kprobe optimizer core, and metadata from ARM checkers (`stack_space`, `register_usage_flags`). Built only for non-Thumb2 `CONFIG_OPTPROBES`.

Risks: branch range and alignment checks are critical; wrong template offsets corrupt saved register layout. Direct execution is unsafe if register usage omitted PC or if the original instruction has side effects incompatible with template restore. Stack protection must account for probed instruction stores below SP.

Test signals: kprobe benchmarks in `test-core.c` include push/pop patterns meant to compare optimized and unoptimized paths; ARM instruction tests and stack checkers provide the metadata this optimizer trusts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/probes/kprobes/opt-arm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/probes/kprobes/test-arm.c -->
# sources/distributed-fs/ceph-client/arch/arm/probes/kprobes/test-arm.c

Purpose: defines the ARM-mode instruction simulation test catalog used by the kprobe test harness. It supplies exhaustive inline assembly cases for supported, unsupported, conditional, branching, memory, stack, and architecture-gated ARM instructions.

Important APIs and macros: exports `kprobe_arm_test_cases()`. Uses `TEST_*` macros from `test-core.h`, `TEST_ARM_TO_THUMB_INTERWORK_R()`, and `TEST_ARM_TO_THUMB_INTERWORK_P()` for ARM-to-Thumb PC-write transitions. Test groups cover data processing, miscellaneous/status instructions, multiply families, synchronization primitives, extra load/store, word/byte load/store, media/parallel arithmetic, packing/saturation/reversal, signed multiplies, bitfields, branches/block transfer, coprocessor/SVC, unconditional/system instructions, and memory hints.

Control flow: the function sequentially emits inline assembly test cases. `TEST_SUPPORTED` and `TEST_UNSUPPORTED` verify registration decisions without executing the instruction as a behavioral comparison. Normal tests execute once without a probe and once with a probe so the harness can compare register, CPSR, memory, and branch target outcomes.

State and persistence: no persistent state beyond setting `kprobe_test_flags = 0`. Test data is encoded inline next to generated assembly and consumed by `test-core.c`.

Dependencies and integration: only built for non-Thumb2 kernels. It depends on architecture version macros to include ARMv5/v6/v7 cases and on `asm/probes.h` opcode helpers for raw encodings.

Risks: test cases encode architectural undefined/unpredictable boundaries and may need updates when decode tables change. Some cases are conditional on CPU architecture, so coverage differs across builds. Literal branch labels and interworking snippets must remain aligned with harness expectations.

Test signals: failures identify either an instruction behavior mismatch, an incorrect accept/reject decision, or missing coverage in `coverage_end()` for the ARM decode table.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/probes/kprobes/test-arm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/probes/kprobes/test-core.c -->
# sources/distributed-fs/ceph-client/arch/arm/probes/kprobes/test-core.c

Purpose: implements the ARM kprobe self-test framework, including API tests, kretprobe tests, optional benchmarking, decode-table consistency checks, decode coverage tracking, and the runtime harness that compares direct instruction execution with probed instruction simulation/emulation.

Important functions: `run_all_tests()`, `run_api_tests()`, `test_kprobe()`, `test_kretprobe()`, `run_benchmarks()`, `table_test()`, `coverage_start()`, `coverage_add()`, `coverage_end()`, `__kprobes_test_case_start()`, `kprobes_test_case_start()`, `setup_test_context()`, `kprobes_test_case_end()`, and result-dump helpers. It also defines pre/post handlers for before, case, and after probes.

Control flow: API tests register probes on small ARM/Thumb functions and verify handler calls and unregister behavior. Instruction tests parse inline metadata emitted by `test-core.h`, register probes around the instruction under test, run a reference execution, insert a probe on the instruction, rerun under varied CPSR/IT scenarios, and compare resulting registers and memory. Coverage logic walks decode tables, marks matched entries, and checks register-class coverage.

State and persistence: maintains test counters, current inline test metadata, expected/result `pt_regs`, expected memory snapshots, active test probes, CPSR scenario state, and coverage tables allocated with `kmalloc`.

Dependencies and integration: depends on kprobe APIs, `core.h`, decode tables, ARM/Thumb opcode helpers, and test case catalogs from `test-arm.c` or `test-thumb.c`. Registered as a module init or `late_initcall`.

Risks: the harness manipulates stack, CPSR, IT state, interrupt masking, and PC values; mistakes can produce false failures or unstable tests. Coverage table capacity is fixed at 256 entries. It ignores CPSR A/F bits because kernel context can vary them.

Test signals: final logs report total simulation tests, pass/fail counts, coverage failures, API failures, and benchmark timings. Any nonzero failure returns `-EINVAL` or another error to module/init infrastructure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/probes/kprobes/test-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/probes/kprobes/test-core.h -->
# sources/distributed-fs/ceph-client/arch/arm/probes/kprobes/test-core.h

Purpose: defines the inline assembly DSL and shared constants used by ARM kprobe instruction test catalogs.

Important APIs and types: declares `struct test_arg`, `struct test_arg_regptr`, `struct test_arg_mem`, and `struct test_arg_end` for inline metadata. Defines argument types (`ARG_TYPE_REG`, `ARG_TYPE_PTR`, `ARG_TYPE_MEM`, `ARG_TYPE_REG_MASKED`), flags (`ARG_FLAG_UNSUPPORTED`, `ARG_FLAG_SUPPORTED`, ISA flags), test flags (`TEST_FLAG_NO_ITBLOCK`, `TEST_FLAG_FULL_ITBLOCK`, `TEST_FLAG_NARROW_INSTR`), and constants such as `TEST_MEMORY_SIZE`, `VAL1`-`VALR`, `HH1`, `HH2`, and `PSR_IGNORE_BITS`.

Control flow: `TESTCASE_START` emits metadata and calls `__kprobes_test_case_start`; `TEST_ARG_*` macros encode register/pointer/memory setup; `TEST_ARG_END` records code/branch/end offsets and switches assembler ISA; `TEST_INSTRUCTION`, `TEST_BRANCH_F/B`, and variants emit the code under test; `TESTCASE_END` calls the ISA-specific end wrapper. Convenience macros compose common argument patterns and supported/unsupported checks.

State and persistence: no runtime storage, but it defines the binary inline data format consumed by `test-core.c`. Global declarations expose `kprobe_test_flags` and `kprobe_test_cc_position`.

Dependencies and integration: used by `test-arm.c` and `test-thumb.c`; declares their entry points depending on `CONFIG_THUMB2_KERNEL` and the test harness wrapper symbols.

Risks: inline metadata layout must match C structs exactly, including padding and offsets. Incorrect clobbers or ISA switches can corrupt the caller. The macros rely on local labels (`0`, `1`, `2`, `50`, `99`) with strict meaning for branch tests.

Test signals: if macro-generated metadata is wrong, `kprobes_test_case_start()` will fail width checks, place probes at wrong addresses, or compare the wrong branch target/memory region.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/probes/kprobes/test-core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/probes/kprobes/test-thumb.c -->
# sources/distributed-fs/ceph-client/arch/arm/probes/kprobes/test-thumb.c

Purpose: defines Thumb-2 kprobe instruction test catalogs for both 16-bit Thumb and 32-bit Thumb encodings.

Important APIs and macros: exports `kprobe_thumb16_test_cases()` and `kprobe_thumb32_test_cases()`. Adds Thumb-specific helpers `DONT_TEST_IN_ITBLOCK()`, `CONDITION_INSTRUCTIONS()`, `TEST_ITBLOCK()`, and `TEST_THUMB_TO_ARM_INTERWORK_P()`. T16 groups cover shifts, data processing, high-register operations, BX/BLX, literal loads, load/store, ADR/SP-relative instructions, CBZ/CBNZ, sign/zero extension, push/pop, IT, LDM/STM, conditional and unconditional branches. T32 groups cover LDM/STM, LDRD/STRD, table branches, data processing, coprocessor rejects, plain binary immediates, branches/control, stores, SIMD rejects, loads/hints, register operations, media, multiply, long multiply, and IT-block tests.

Control flow: like the ARM catalog, each macro emits inline metadata and code for the shared harness. T16 starts with `TEST_FLAG_NARROW_INSTR`; T32 clears it. Conditional instruction groups set `kprobe_test_cc_position` so the harness can decide whether the probe should execute under CPSR/IT combinations.

State and persistence: modifies global test flags while emitting certain groups; no long-lived state beyond inline case data.

Dependencies and integration: built only for `CONFIG_THUMB2_KERNEL`. Uses Thumb raw opcode helpers and relies on the harness to validate instruction width, IT-state behavior, and interworking.

Risks: Thumb PC values, alignment, BLX state switches, IT-state encodings, and 16/32-bit width checks are easy to regress. Some unsupported raw encodings protect decoder boundaries and must stay synchronized with decode tables.

Test signals: failures distinguish wrong T16/T32 instruction-width classification, incorrect simulated branch/interworking target, IT conditional execution errors, unsupported instruction acceptance, or missing decode coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/probes/kprobes/test-thumb.c -->
