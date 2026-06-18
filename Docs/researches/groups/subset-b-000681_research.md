# subset-b-000681 ARM64 kernel research

Grouped research for `subset-b-000681`. Each section is source-tree aligned and is intended to be split into `Docs/researches/<source>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/pi/patch-scs.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kernel/pi/patch-scs.c

Purpose: this early position-independent helper converts PACIASP/AUTIASP return-address signing instructions into shadow-call-stack push/pop instructions when dynamic SCS is enabled. It does so before the normal kernel relocation environment exists, using a deliberately small DWARF `.eh_frame` parser to locate the instructions that are paired with `DW_CFA_negate_ra_state`.

Important APIs and state: `dynamic_scs_is_enabled` is the exported boot-time state bit. `scs_patch()` is the public entry point declared by `pi.h`; it walks CIE/FDE records, validates the CIE augmentation is exactly `zR`, tracks `code_alignment_factor`, and supports pcrel `sdata4` and `sdata8` FDE encodings. `scs_handle_fde_frame()` advances a code location according to supported CFA opcodes and calls `scs_patch_loc()` on return-address-state toggles. `scs_patch_loc()` recognizes literal opcodes for `PACIASP`, `AUTIASP`, `SCS_PUSH`, and `SCS_POP`, writes little-endian AArch64 instructions, and performs data-cache maintenance using either `dc civac` or an IDC-aware alternative.

Control flow: `scs_patch()` parses one frame at a time. CIE records set parser configuration; FDE records are parsed first as a dry run unless `skip_dry_run` requests direct patching, then parsed again to mutate instruction text. Within an FDE, augmentation payload length is treated as a single-byte ULEB128; frame opcodes that do not affect code location are skipped, location-advance opcodes update `loc`, and unsupported opcodes abort with `EDYNSCS_*` errors. The patch target is `loc - 4` because the CFI toggle follows the PAC instruction.

Dependencies and integration: depends on ARM64 SCS definitions, early PI `offset_to_ptr()` behavior from included boot headers, Linux endian helpers, and alternative patching macros. It integrates with early kernel mapping and relocation code that can still safely patch kernel text before normal alternatives/ftrace machinery.

Risks: malformed `.eh_frame` input could produce wrong patch addresses, so the parser is intentionally restrictive. The code assumes Linux-generated CFI layout and rejects unexpected CIE or CFA patterns. Cache maintenance is essential because patched instructions may execute soon after early boot mapping changes. The dry-run phase is a useful guard against partial text mutation.

Test signals: build-time coverage comes from generated `.eh_frame` shape and config combinations for SCS, pointer authentication, and cache-IDC workarounds. Runtime failures would usually appear as early boot errors, invalid dynamic-SCS error codes, return-address corruption, or boot hangs after patched prologues/epilogues execute.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/pi/patch-scs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/pi/pi.h -->
# sources/distributed-fs/ceph-client/arch/arm64/kernel/pi/pi.h

Purpose: this header centralizes declarations for ARM64 position-independent early boot code. It provides helpers for place-relative data references and declares the early mapping, relocation, KASLR, feature-override, dynamic SCS, and page-table construction entry points used before the fully relocated kernel is running.

Important APIs and types: `prel64_t` is a volatile signed long used for 64-bit place-relative references. `PREL64(type, name)` stores either a typed pointer or its `prel64` representation, while `prel64_pointer()` converts a `*_prel` field back to a typed pointer using `prel64_to_pointer()`. The `__prel64_initconst` section marker places such data in `.init.rodata.prel64`, which `relacheck.c` permits and rewrites from ABS64 to PREL64. Extern declarations expose `dynamic_scs_is_enabled`, `init_idmap_pg_dir`, `init_pg_dir`, `init_feature_override()`, `kaslr_early_init()`, `relocate_kernel()`, `scs_patch()`, `map_range()`, `early_map_kernel()`, and `create_init_idmap()`.

Control flow and state: `prel64_to_pointer()` returns `NULL` for a zero offset, otherwise returns `offset + *offset`. This lets early boot code dereference data even before absolute relocations are fully applied. The header itself has no persistence, but it defines the contract for early boot global page directories and the dynamic SCS flag.

Dependencies and integration: included by files in `arch/arm64/kernel/pi/`, especially relocation, early ID-register overrides, mapping, and SCS patching. It depends on core ARM64 page-table and Linux integer types being visible via surrounding translation units.

Risks: users must only apply `prel64_pointer()` to fields declared with `PREL64`; mixing absolute and place-relative storage breaks early relocation assumptions. The volatile `prel64_t` prevents undesirable compiler assumptions, but does not protect against incorrect section placement. The header is part of the early boot ABI, so signature changes ripple into assembly and boot mapping code.

Test signals: successful all-config ARM64 builds, relacheck acceptance of `.rodata.prel64`, and early boot through KASLR/relocation paths are the main signals. Failures manifest as link-time relocation guard errors, early NULL/wrong-pointer dereferences, or boot stalls in early mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/pi/pi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/pi/relacheck.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kernel/pi/relacheck.c

Purpose: this host-side build utility validates relocation records in early position-independent ARM64 objects. It rejects unexpected absolute 64-bit relocations in allocatable non-executable data and converts allowed `.rodata.prel64` absolute relocations to `R_AARCH64_PREL64`.

Important APIs and state: the process-level globals `ehdr`, `shdr`, `strtab`, and `swap` hold the mapped ELF header, section headers, string table, and endian-conversion flag. `swab_elfxword()`, `swab_elfword()`, and `swab_elfhword()` abstract host/target byte order. `main()` opens the temporary object passed as `argv[1]`, mmaps it writable/shared, scans `SHT_RELA` sections, and reports errors using `argv[2]` as the display name.

Control flow: after argument and file setup, `main()` chooses `swap` by comparing ELF data encoding to host order. For each RELA section, it examines the target section via `sh_info`; only allocatable data sections, not executable sections, are guarded. If the target section name contains `.rodata.prel64`, ABS64 relocations are rewritten in-place by toggling the relocation type bits from `R_AARCH64_ABS64` to `R_AARCH64_PREL64`. Otherwise an ABS64 relocation is a fatal error: the tool prints a diagnostic, closes and unlinks the object, and exits failure.

Dependencies and integration: uses libc, POSIX file/mmap APIs, and ELF constants. It is intended for the kernel build pipeline around the `pi/` objects, pairing with `pi.h` and `__prel64_initconst` to enforce early relocation discipline.

Risks: the utility trusts basic ELF layout enough to mmap and index headers, so it is for controlled build inputs rather than hostile files. The `.rodata.prel64` match is substring based but scoped to the target section name. Unlinking the temporary output is intentional build hygiene but can obscure later inspection if logs are insufficient.

Test signals: build failure on new accidental absolute references is the primary signal. Positive tests include `.rodata.prel64` entries being converted and endian-swapped objects being handled correctly. Changes should be checked by inspecting relocations with `readelf -r` before and after the tool.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/pi/relacheck.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/pi/relocate.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kernel/pi/relocate.c

Purpose: this early boot routine applies relative relocations to the kernel image after a runtime offset is chosen. It supports classic RELA relative relocations and compressed RELR relative relocations.

Important APIs and state: `relocate_kernel(u64 offset)` is the single exported entry point. Linker-provided ranges `rela_start`/`rela_end` and `relr_start`/`relr_end` identify relocation tables. A local `place` pointer tracks the current RELR relocation word while decoding bitmap entries.

Control flow: the function first scans every `Elf64_Rela` record and applies only `R_AARCH64_RELATIVE` relocations by writing `r_addend + offset` to `r_offset + offset`. If `CONFIG_RELR` is disabled or `offset` is zero, it returns after RELA. Otherwise it decodes RELR: even entries are base addresses to relocate and advance from; odd entries are bitmaps for up to 63 subsequent machine words, with each set bit adding the offset to the corresponding word.

Dependencies and integration: called by early PI mapping/relocation code declared in `pi.h`, and depends on linker script symbols for relocation table boundaries. It assumes the image is mapped writable at the offset-adjusted addresses and that only relative relocation types need early application.

Risks: RELR decoding is compact but sensitive to `place` sequencing; malformed or unsorted RELR data would relocate wrong addresses. The implementation intentionally ignores non-relative RELA records because other relocation classes are either forbidden by build checks or handled elsewhere. Running with `offset == 0` skips RELR because adding zero is unnecessary.

Test signals: KASLR boot with nonzero offsets, `CONFIG_RELR` builds, and relocation test modules provide coverage. Failures generally appear as early boot crashes, bad global pointers, or corrupted data after relocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/pi/relocate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/pointer_auth.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kernel/pointer_auth.c

Purpose: this file implements ARM64 pointer-authentication user ABI controls used by `prctl()` and ptrace regsets. It resets per-task PAC keys and enables or disables address-auth key use through the user SCTLR shadow.

Important APIs and state: `ptrauth_prctl_reset_keys()` resets all or selected keys in `task->thread.keys_user`, using `get_random_bytes()` and installing keys for the current task. `ptrauth_set_enabled_keys()` updates `task->thread.sctlr_user` bits corresponding to `PR_PAC_APIAKEY`, `APIBKEY`, `APDAKEY`, and `APDBKEY`. `ptrauth_get_enabled_keys()` exports the enabled-key mask. `arg_to_enxx_mask()` maps prctl bits to `SCTLR_ELx_ENIA/ENIB/ENDA/ENDB`.

Control flow: reset rejects unsupported hardware, compat tasks, unknown bits, and attempts to reset unavailable address or generic keys. Key enable changes validate `enabled` is a subset of `keys`, then update `sctlr_user` with preemption disabled; if the target is current, `update_sctlr_el1()` is called in the same critical section so context switch code cannot observe mismatched software/hardware state.

Dependencies and integration: relies on `system_supports_address_auth()`, `system_supports_generic_auth()`, ARM64 pointer-auth helpers, `update_sctlr_el1()` in `process.c`, and user ABI constants from `linux/prctl.h`. `ptrace.c` uses these routines for `NT_ARM_PAC_ENABLED_KEYS`.

Risks: PAC is unavailable for compat threads, so callers must propagate `-EINVAL` correctly. SCTLR updates are ordering-sensitive; moving preemption boundaries could race with `__switch_to()`. Key resets alter process security state and must not be accepted on unsupported CPUs.

Test signals: user ABI tests for `PR_PAC_RESET_KEYS`, `PR_PAC_SET_ENABLED_KEYS`, ptrace PAC regsets, checkpoint/restore, and mixed compat/native tasks. Runtime signs include correct PAC enable masks in ptrace and no kernel PAC disable while executing kernel code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/pointer_auth.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/probes/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm64/kernel/probes/Makefile

Purpose: this Makefile selects ARM64 probe support objects based on kernel configuration. It binds the shared decoder/simulator code into both kprobes and uprobes builds.

Important build rules: `obj-$(CONFIG_KPROBES)` includes `kprobes.o`, `decode-insn.o`, `kprobes_trampoline.o`, and `simulate-insn.o`. `obj-$(CONFIG_UPROBES)` includes `uprobes.o`, `decode-insn.o`, and `simulate-insn.o`.

Control flow and integration: there is no runtime control flow, but the object composition is significant. Kprobes need the text patching handlers and kretprobe trampoline; uprobes reuse the same instruction classification and simulation layer without the kernel text breakpoint machinery.

Dependencies: depends on Kbuild config symbols and on the C/assembly files in the same directory. Shared objects must remain free of kprobes-only dependencies unless protected by `CONFIG_KPROBES`, because they are also linked for uprobes.

Risks: adding a dependency to `decode-insn.o` or `simulate-insn.o` that only exists under one probe config can break the other. Omitting `kprobes_trampoline.o` breaks kretprobes, while omitting simulator support rejects branch/literal instructions that cannot run from XOL slots.

Test signals: build matrices for `CONFIG_KPROBES`, `CONFIG_UPROBES`, both, and neither. Runtime validation comes from kprobe/uprobe selftests, kretprobe return trapping, and probe registration on simulated versus single-stepped instructions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/probes/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/probes/decode-insn.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kernel/probes/decode-insn.c

Purpose: this file classifies AArch64 instructions for kprobes and uprobes. It decides whether an instruction can safely execute out-of-line in an XOL slot, must be simulated in the exception handler, or must be rejected.

Important APIs: `arm_probe_decode_insn()` is shared by kprobes and uprobes; it returns `INSN_GOOD`, `INSN_GOOD_NO_SLOT`, or `INSN_REJECTED` and fills `arch_probe_insn.handler` for simulated instructions. Under `CONFIG_KPROBES`, `arm_kprobe_decode_insn()` adds kernel-specific handling for literal loads and atomic exclusive sequences. `aarch64_insn_is_steppable()` encodes the safety policy for XOL execution.

Control flow: NOPs are simulated for speed. Branch/system-class instructions are rejected from XOL if they branch, touch MSR/MRS in unsafe ways, throw exceptions, return from exception, or are unsafe hints. Literal loads, exclusive operations, and memory copy/set sequences are also not XOL-safe. Known non-steppable instructions are mapped to simulator handlers for conditional branches, compare/test branches, ADR/ADRP, direct/indirect branches, returns, and literal loads. Kprobes additionally scans backward within the current symbol up to `MAX_ATOMIC_CONTEXT_SIZE` to reject probes between load-exclusive and store-exclusive.

Dependencies and integration: heavily depends on `asm/insn.h` decoders, `simulate-insn.h` handlers, kallsyms symbol size/offset lookup, and `decode-insn.h` enum contracts. `kprobes.c` and `uprobes.c` call into this before installing probes.

Risks: incorrect classification can corrupt PC-relative behavior, exclusive sequences, system register state, or exception control flow. Atomic scanning depends on kallsyms boundaries to avoid searching unrelated text or literals. New ARM64 instructions must be considered here before being probed safely.

Test signals: probe selftests registering on branches, literal loads, NOPs, exclusive sequences, MOPS, and system instructions. Failures show as rejected valid probes, accepted unsafe probes, wrong post-probe PC, or unexpected faults in XOL slots.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/probes/decode-insn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/probes/decode-insn.h -->
# sources/distributed-fs/ceph-client/arch/arm64/kernel/probes/decode-insn.h

Purpose: this private header defines the ARM64 probe instruction decoding contract shared by kprobes and uprobes.

Important APIs and types: `MAX_ATOMIC_CONTEXT_SIZE` is fixed at 128 bytes divided by instruction size, matching Arm guidance for load-exclusive/store-exclusive sequences. `enum probe_insn` defines `INSN_REJECTED`, `INSN_GOOD_NO_SLOT`, and `INSN_GOOD`. It declares `arm_probe_decode_insn()` for shared decode/simulation decisions and `arm_kprobe_decode_insn()` under `CONFIG_KPROBES` for kernel-specific checks.

Control flow and state: the header has no runtime state. Its enum values drive allocation and execution paths in `kprobes.c` and `uprobes.c`: rejected instructions fail registration, good-no-slot instructions run via simulator handlers, and good instructions use XOL slots.

Dependencies and integration: includes `asm/kprobes.h` for architecture probe structures and `__kprobes` annotations. It integrates with `decode-insn.c`, `kprobes.c`, and `uprobes.c`.

Risks: changing enum semantics requires coordinated changes in both kprobe and uprobe users. The atomic context size is a policy boundary; shrinking or expanding it changes which kernel instructions can be instrumented.

Test signals: compile coverage with `CONFIG_KPROBES` enabled/disabled and functional probes on instruction classes whose decode result should differ.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/probes/decode-insn.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/probes/kprobes.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kernel/probes/kprobes.c

Purpose: this is the ARM64 backend for kernel kprobes and kretprobes. It allocates executable instruction slots, installs breakpoint instructions into kernel text, manages per-CPU active probe state, handles breakpoint/single-step exceptions, and implements return-probe trampoline handling.

Important APIs and state: per-CPU `current_kprobe` and `kprobe_ctlblk` track active and nested probes. `alloc_insn_page()` allocates ROX kprobe XOL memory. `arch_prepare_kprobe()` validates alignment, excludes exception-table addresses, decodes the instruction, allocates an XOL slot when needed, and prepares either single-step or simulation metadata. `arch_arm_kprobe()` and `arch_disarm_kprobe()` patch text with `BRK64_OPCODE_KPROBES` or the original opcode. Exception handlers include `kprobe_brk_handler()`, `kprobe_ss_brk_handler()`, `kprobe_fault_handler()`, and `kretprobe_brk_handler()`.

Control flow: a probe hit sets the current per-CPU probe, runs the pre-handler if present, then either redirects PC to the XOL slot with DAIF masked or calls the simulator and immediately performs post handling. The XOL slot contains the original instruction followed by an ARM64 kprobe single-step breakpoint. On the single-step breakpoint, the handler restores DAIF, fixes PC to `xol_restore` for non-branching instructions, invokes the post-handler, and clears probe state. Nested hits are allowed only from specific states and otherwise BUG. Faults during XOL execution rewind PC to the original probe address and let normal fault handling proceed.

Dependencies and integration: depends on text patching, debug monitor hooks, exception tables, execmem, per-CPU kprobe core state, and the instruction decoder. `arch_populate_kprobe_blacklist()` blocks entry, irqentry, hyp, and hyp-idmap text ranges. Kretprobes replace LR with `__kretprobe_trampoline`, handled by `kretprobe_brk_handler()`.

Risks: per-CPU state requires interrupts masked while executing XOL to avoid migration/nesting surprises. Text patching and cache maintenance ordering are critical. Reentrancy bugs are fatal. Blacklist gaps could allow probes in code that cannot tolerate breakpoint exceptions.

Test signals: kprobes/kretprobes selftests, blacklist contents in debugfs, probes on simulated and XOL instructions, fault-in-probe tests, and nested probe stress. Bad behavior appears as missed probes, bad PC restore, WARN/BUG in reentry, or crashes in exception entry code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/probes/kprobes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/probes/kprobes_trampoline.S -->
# sources/distributed-fs/ceph-client/arch/arm64/kernel/probes/kprobes_trampoline.S

Purpose: this assembly file defines the ARM64 kretprobe trampoline target. Kretprobes replace a function return address with this symbol so a breakpoint exception can route return handling through the kprobe core.

Important symbols: `__kretprobe_trampoline` is emitted with `SYM_CODE_START/END`. It executes `brk #KRETPROBES_BRK_IMM`, then `ASM_BUG()` as a non-return fallback.

Control flow: normal execution should never proceed past the `brk`. The exception is recognized by `kretprobe_brk_handler()` in `kprobes.c`, which checks that `regs->pc` equals the trampoline symbol, calls `kretprobe_trampoline_handler()` with the frame pointer, and replaces PC with the original return destination.

Dependencies and integration: includes Linux linkage, assembler, and bug macros. It is linked only when `CONFIG_KPROBES` is enabled by the probes Makefile.

Risks: the trampoline must remain minimal and placed in executable kernel text. Any instruction after the BRK is defensive only; reaching it indicates the debug hook failed to claim the kretprobe breakpoint.

Test signals: kretprobe tests should show return handlers firing and no execution of `ASM_BUG()`. Symbol lookup and blacklist behavior should prevent normal probes from corrupting the trampoline path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/probes/kprobes_trampoline.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/probes/simulate-insn.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kernel/probes/simulate-insn.c

Purpose: this file simulates selected AArch64 instructions for kprobes and uprobes when executing them from an XOL slot would produce wrong PC-relative behavior or unsafe side effects.

Important APIs: simulator functions include `simulate_adr_adrp()`, `simulate_b_bl()`, `simulate_b_cond()`, `simulate_br_blr()`, `simulate_ret()`, `simulate_cbz_cbnz()`, `simulate_tbz_tbnz()`, `simulate_ldr_literal()`, `simulate_ldrsw_literal()`, and `simulate_nop()`. Helpers read/write pt_regs, compute signed displacements, and update LR through `update_lr()`.

Control flow: each simulator decodes register fields and immediates directly from the 32-bit opcode, mutates `pt_regs`, and sets PC to the architecturally expected next address or branch target. Branch-with-link and branch-register-with-link call `update_lr()`. Returns call `simulate_ret()`. Conditional branch simulators evaluate pstate or register bits before choosing fallthrough versus target. Literal loads read from the original instruction address plus displacement and write the target general register.

State and integration: state is entirely in `pt_regs` plus current-task guarded control stack state. When GCS is enabled for EL0, link updates push to user GCS and returns pop/validate it, forcing `SIGSEGV` on mismatch or access errors. The simulator is selected by `decode-insn.c` and invoked by `kprobes.c`/`uprobes.c`.

Risks: simulator correctness is ABI-critical; off-by-one displacement or register-width mistakes change user/kernel control flow. Literal load simulation dereferences original kernel text/data addresses for kprobes. GCS interactions can intentionally signal user tasks if a simulated call/return violates shadow-stack expectations.

Test signals: probe tests on ADR/ADRP, branches, BL/BLR, RET, CBZ/CBNZ, TBZ/TBNZ, LDR literal, and NOP. GCS-enabled uprobe tests should validate link/return shadow-stack behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/probes/simulate-insn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/probes/simulate-insn.h -->
# sources/distributed-fs/ceph-client/arch/arm64/kernel/probes/simulate-insn.h

Purpose: this private header declares the ARM64 probe instruction simulator entry points used by the decoder and probe handlers.

Important APIs: it declares one function per simulated instruction family: ADR/ADRP, B/BL, conditional branch, BR/BLR, RET, CBZ/CBNZ, TBZ/TBNZ, LDR literal, LDRSW literal, and NOP. Each takes `u32 opcode`, original instruction address as `long addr`, and mutable `struct pt_regs *regs`.

Control flow and state: no local state. The common signature lets `arch_probe_insn.handler` point at any simulator function and lets kprobe/uprobe code invoke the handler uniformly.

Dependencies and integration: included by `decode-insn.c` to assign handlers and by `simulate-insn.c` for declarations. Callers must provide pt_regs from the active exception context.

Risks: adding a simulator in C without declaring it here prevents the decoder from assigning it cleanly. Changing the signature breaks the handler callback ABI embedded in architecture probe structs.

Test signals: all simulator functions should be referenced by decode paths and covered by probe registration/execution tests for their instruction families.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/probes/simulate-insn.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/probes/uprobes.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kernel/probes/uprobes.c

Purpose: this is the ARM64 backend for uprobes. It copies user instructions into XOL slots, validates probed instructions, controls user single-step state, simulates unsupported-XOL instructions, and handles uretprobe return-address hijacking including GCS support.

Important APIs: `arch_uprobe_copy_ixol()` writes and cache-syncs the XOL page. `arch_uprobe_analyze_insn()` rejects AArch32 and unaligned probes, then decodes the instruction and marks simulation. `arch_uprobe_pre_xol()`, `arch_uprobe_post_xol()`, `arch_uprobe_abort_xol()`, and `arch_uprobe_skip_sstep()` manage XOL/simulation execution. `arch_uretprobe_hijack_return_addr()` replaces LR and, when GCS is enabled, updates the user guarded control stack. Breakpoint hooks are `uprobe_brk_handler()` and `uprobe_single_step_handler()`.

Control flow: registration decodes the instruction using the shared decoder. On hit, pre-XOL sets `thread.fault_code` to a sentinel, redirects PC to `utask->xol_vaddr`, and enables single step. Post-XOL asserts the XOL instruction itself did not trap, moves PC to `utask->vaddr + 4`, and disables stepping. Simulated instructions bypass XOL and invoke the selected handler at the current PC. Abort rewinds PC to the probed address.

State and dependencies: uses `current->utask`, `current->thread.fault_code`, user debug single-step controls, cache alias maintenance, highmem local mapping, and GCS helpers. Uretprobes compare LR and GCS top before replacing the return address with the trampoline to avoid creating an impossible GCS return.

Risks: no AArch32 probing is supported. XOL fault detection depends on the sentinel fault code. GCS mismatch causes the return probe to abort by returning `-1` as the original return address. Cache maintenance must run when an XOL slot changes.

Test signals: uprobes and uretprobes selftests on branch simulation, XOL faults, signal aborts, and GCS-enabled return probes. Failures include stuck single-step state, wrong PC after XOL, or SIGSEGV from invalid GCS updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/probes/uprobes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/process.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kernel/process.c

Purpose: this file implements ARM64 process and CPU lifecycle glue: reboot/halt/poweroff, register dumping, thread flush/duplication, fork setup, context switching, stack alignment, new-exec architecture setup, tagged-address/MTE controls, and PR_TSC controls.

Important APIs and state: exported state includes `pm_power_off`, optional `__stack_chk_guard`, and per-CPU `__entry_task`. System lifecycle functions include `machine_shutdown()`, `machine_halt()`, `machine_power_off()`, and `machine_restart()`. Task lifecycle functions include `flush_thread()`, `arch_dup_task_struct()`, `arch_release_task_struct()`, `copy_thread()`, `tls_preserve_current_state()`, and `__switch_to()`. User ABI helpers include `set_tagged_addr_ctrl()`, `get_tagged_addr_ctrl()`, `get_tsc_mode()`, `set_tsc_mode()`, and `arch_elf_adjust_prot()`.

Control flow: fork copies current pt_regs for user tasks or synthesizes kernel-thread regs, initializes kernel PAC keys, snapshots TLS/POE state, handles CLONE_SETTLS, conditionally inherits SME ZA/TPIDR2 for fork but not CLONE_VM threads, allocates GCS stack state, and sets the CPU context to `ret_from_fork`. Context switching is ordered: debug state check, FPSIMD, TLS, breakpoints, context ID, entry task, SSBS, counter access, pointer auth, POE, GCS, full `dsb(ish)`, MTE, user SCTLR update, MPAM, then `cpu_switch_to()`.

State and persistence: per-task architecture state lives under `thread_struct`: TLS, FP/SVE/SME storage, PAC keys and `sctlr_user`, POE `por_el0`, GCS metadata, breakpoint state, MTE flags, and TSC trapping flags. `flush_thread()` resets user-exposed state on exec. The tagged-address sysctl `abi.tagged_addr_disabled` only blocks future opt-in.

Dependencies and integration: integrates with scheduler, reboot, EFI, SMP, FPSIMD/SVE/SME, PAC, GCS, MTE, MPAM, hw breakpoints, compat mode, ELF loader, prctl, sysctl, and timer errata. `pointer_auth.c`, `ptrace.c`, and `signal.c` rely on these helpers for state synchronization.

Risks: context-switch order is correctness-critical for speculation mitigations, lazy FP state, MTE asynchronous faults, and PAC SCTLR updates. Fork handling must avoid sharing stale SVE/SME buffers. Tagged-address and TSC controls are ABI-visible and must reject compat tasks where unsupported.

Test signals: fork/clone/exec tests across native and compat tasks, MTE/tagged address prctl tests, PAC/GCS/SME context-switch tests, CPU hotplug and kexec/reboot paths, and ptrace mutation of FP/TLS state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/process.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/proton-pack.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kernel/proton-pack.c

Purpose: this file detects, reports, and enables ARM64 mitigations for Spectre v1, v2, v3a, v4/SSBD, and Spectre-BHB. It coordinates CPU feature detection, firmware SMCCC calls, vector patching, per-task prctl policy, and sysfs vulnerability strings.

Important APIs and state: global mitigation states include `spectre_v2_state`, `spectre_v4_state`, and `spectre_bhb_state`, updated monotonically by `update_mitigation_state()`. Per-CPU state includes `bp_hardening_data` and `arm64_ssbd_callback_required`. Public hooks include `cpu_show_spectre_v1()`, `cpu_show_spectre_v2()`, `cpu_show_spec_store_bypass()`, `has_spectre_v2()`, `spectre_v2_enable_mitigation()`, `has_spectre_v3a()`, `spectre_v3a_enable_mitigation()`, `has_spectre_v4()`, `spectre_v4_enable_mitigation()`, `spectre_v4_enable_task_mitigation()`, `arch_prctl_spec_ctrl_get/set()`, `is_spectre_bhb_affected()`, `spectre_bhb_enable_mitigation()`, and alternative patch callbacks.

Control flow: boot parameters (`nospectre_v2`, `ssbd=`, `nospectre_bhb`) set policy early. V2 first checks hardware CSV2/safe-list, then firmware workaround 1 and optional CPU-specific link-stack sanitization. V4 checks safelists, SSBS hardware, firmware workaround 2, and per-task prctl state. BHB chooses between ECBHB, ClearBHB instruction, branchy loop, firmware workaround 3, or vulnerability, and selects EL1/KVM hardening vectors. Alternative patch callbacks replace NOP/branch/MOV instructions based on final mitigation choices.

State and integration: mitigation state is global/per-CPU and should not worsen after capabilities finalize. Per-task store-bypass state is stored in task speculation flags and `TIF_SSBD`; context switch code in `process.c` calls `spectre_v4_enable_task_mitigation()`.

Dependencies: SMCCC, CPU MIDR/ftr helpers, alternative patching, vectors, KVM hyp vector slots, BPF sysctl for unprivileged eBPF reporting, and prctl speculation controls.

Risks: mixed big.LITTLE systems can have heterogeneous mitigation support; late CPU onlining after finalized capabilities is guarded. Incorrect vector selection or firmware conduit patching can leave entry paths unmitigated. User-visible prctl policy must respect force-on/off semantics.

Test signals: sysfs vulnerability files, boot logs for disabled mitigations, CPU hotplug with mixed cores, prctl store-bypass tests, BPF warning path, and alternative-patching validation for BHB/SSBD vectors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/proton-pack.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/psci.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kernel/psci.c

Purpose: this file provides ARM64 `cpu_operations` backed by PSCI firmware calls. It is responsible for preparing, booting, disabling, powering off, and polling secondary CPUs when PSCI is the selected CPU bring-up mechanism.

Important APIs and state: `cpu_psci_ops` exposes `.cpu_init`, `.cpu_prepare`, `.cpu_boot`, and, with hotplug, `.cpu_can_disable`, `.cpu_disable`, `.cpu_die`, and `.cpu_kill`. The implementation uses global `psci_ops` callbacks and `cpu_logical_map()` MPIDR values.

Control flow: prepare verifies `psci_ops.cpu_on` exists. Boot calls `cpu_on(cpu_logical_map(cpu), __pa_symbol(secondary_entry))` and logs failures except `-EPERM`. Hotplug disable rejects missing `cpu_off` and CPUs where a trusted OS is resident. Die calls PSCI `cpu_off()` with a power-down state. Kill optionally polls `affinity_info()` for up to about 100 ms until firmware reports the CPU off.

Dependencies and integration: integrates with generic SMP CPU ops, PSCI DT/ACPI initialization from setup, ARM64 secondary entry code, jiffies delays, and trusted-OS residency helpers.

Risks: PSCI availability and firmware behavior dominate correctness. `cpu_kill()` can race with `cpu_die()`, so it polls rather than assuming immediate state. Systems lacking `affinity_info` cannot verify shutdown. Trusted OS residency can prevent CPU offlining.

Test signals: SMP boot, CPU hotplug online/offline cycles, PSCI error logs, and suspend/kexec interactions. Firmware conformance issues show as failed boot of secondary CPUs or timeout warnings during hotplug.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/psci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/ptrace.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kernel/ptrace.c

Purpose: this file implements ARM64 ptrace register access, hardware breakpoint/watchpoint regsets, native and compat regset views, PAC/tagged-address/POE/GCS state access, MTE tag ptrace requests, syscall tracing, and user register validation.

Important APIs and state: public helpers include `regs_query_register_offset()`, `regs_get_kernel_stack_nth()`, `ptrace_disable()`, `flush_ptrace_hw_breakpoint()`, `ptrace_hw_copy_thread()`, `task_user_regset_view()`, `arch_ptrace()`, `compat_arch_ptrace()`, `syscall_trace_enter()`, `syscall_trace_exit()`, and `valid_user_regs()`. The main regset tables are `aarch64_regsets`, `aarch32_regsets`, and `aarch32_ptrace_regsets`. Optional regsets expose FPMR, SVE, streaming SVE, ZA, ZT, PAC masks/keys, tagged-address control, POE, and GCS.

Control flow: get/set handlers synchronize live architectural state before exposing or mutating it. FPSIMD/SVE/SME setters flush task FP state and allocate vector storage as needed. SVE/SME headers validate vector length and payload layout, rejecting mismatched actual VL. Hardware breakpoint regsets lazily allocate perf breakpoints, validate control fields by note type, and use nospec index masking. Compat ptrace converts AArch32 GPR, VFP, TLS, syscall, and hardware breakpoint requests into regset/perf operations.

State and persistence: ptrace reads/writes `task_pt_regs()`, `thread.uw.fpsimd_state`, `thread.sve_state`, `thread.sme_state`, `thread.keys_user`, `thread.sctlr_user`, `thread.por_el0`, `thread.gcs_*`, and `thread.debug` breakpoint arrays. PAC key checkpoint/restore regsets directly serialize 128-bit key halves when configured.

Dependencies and integration: depends on generic ptrace/regset, perf hardware breakpoints, FPSIMD/SVE/SME, PAC, MTE, GCS, POE, audit, seccomp, syscall tracepoints, rseq, and signal register validation. `process.c` and `signal.c` share validation and state synchronization expectations.

Risks: ptrace is a privileged ABI surface; setters must reject invalid pstate, unsupported features, bad vector layouts, unknown GCS flags, and invalid breakpoints. Syscall tracing intentionally clobbers x7/r12 during stops and restores it, which is ABI-observable. Failure to flush/sync FP state can resurrect stale vector data.

Test signals: kernel selftests under `tools/testing/selftests/arm64/abi` and `fp`, ptrace syscall-stop tests, MTE tag peek/poke, hardware breakpoint tests, compat ptrace tests, and checkpoint/restore PAC key tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/ptrace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/reloc_test_core.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kernel/reloc_test_core.c

Purpose: this loadable module drives ARM64 relocation tests by calling assembly helpers that exercise absolute, MOVW, ADR/ADRP, and PREL relocation forms and comparing returned values against expected symbols.

Important APIs and state: `sym64_rel` is a real relocatable data symbol. `SET_ABS()` creates absolute symbols `sym64_abs`, `sym32_abs`, and `sym16_abs`. The `funcs[]` table names each relocation form, stores a function pointer to the assembly helper, and records the expected result. `reloc_test_init()` logs each result and pass/fail status; `reloc_test_exit()` is empty.

Control flow: module init prints a header, iterates the table, calls each helper, compares the return value with the expected absolute or relative address, and logs a detailed error for mismatches. The module still returns success, using logs as the test signal.

Dependencies and integration: pairs with `reloc_test_syms.S` for relocation-emitting code and with module loader relocation handling. It references `memstart_addr` for a far ADRP case.

Risks: expectations are architecture/linker-specific and validate relocation behavior rather than functional kernel logic. Since mismatches do not fail module load, automated test harnesses must parse logs or be extended to assert failure.

Test signals: `pr_info("pass")`/`"fail"` lines after loading the module. Coverage includes ABS64/32/16, signed and unsigned MOVW absolute relocations, ADRP near/far, ADR, and PREL64/32/16.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/reloc_test_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/reloc_test_syms.S -->
# sources/distributed-fs/ceph-client/arch/arm64/kernel/reloc_test_syms.S

Purpose: this assembly file emits the relocation forms consumed by `reloc_test_core.c`. Each symbol returns a value that should reflect the linker/module loader's handling of a specific ARM64 relocation type.

Important symbols: functions include `absolute_data64`, `absolute_data32`, `absolute_data16`, `signed_movw`, `unsigned_movw`, `relative_adrp`, `relative_adrp_far`, `relative_adr`, `relative_data64`, `relative_data32`, and `relative_data16`.

Control flow: absolute-data helpers load embedded `.quad`, `.long`, or `.short` values referring to absolute symbols. MOVW helpers construct an absolute symbol address via `movz/movk` relocation modifiers. ADRP/ADR helpers materialize addresses of `sym64_rel` or `memstart_addr`. PREL helpers load signed relative data from inline constants and add the location address to reconstruct the target.

Dependencies and integration: assembled into the relocation test module. It depends on AArch64 relocation syntax supported by the assembler and on symbol definitions in `reloc_test_core.c`.

Risks: alignment and `.space` directives intentionally shape ADRP reach and page boundaries; changing them can weaken the test. Return values are raw `x0` results and must match the expectations table exactly.

Test signals: used only through the module init log in `reloc_test_core.c`. Disassembly and `readelf -r` should show the relocation classes named in the C table.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/reloc_test_syms.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/relocate_kernel.S -->
# sources/distributed-fs/ceph-client/arch/arm64/kernel/relocate_kernel.S

Purpose: this assembly routine performs the kexec relocation copy and jumps to the new kernel. It is placed in `.kexec_relocate.text` so `machine_kexec()` can copy it to safe memory before the old kernel image is overwritten.

Important symbols and macros: `arm64_relocate_new_kernel` is the exported routine. `turn_off_mmu` programs `INIT_SCTLR_EL1_MMU_OFF`, runs `pre_disable_mmu_workaround`, writes `sctlr_el1`, and issues an ISB. The routine consumes `struct kimage` offsets such as `KIMAGE_START`, `KIMAGE_HEAD`, `KIMAGE_ARCH_TTBR1`, `KIMAGE_ARCH_ZERO_PAGE`, `KIMAGE_ARCH_DTB_MEM`, `KIMAGE_ARCH_EL2_VECTORS`, and `KIMAGE_ARCH_PHYS_OFFSET`.

Control flow: it first loads every needed `kimage` field before memory may be clobbered. It switches the linear map copy with break-before-make support, walks the kexec indirection list, tracks source, destination, and indirection entries, copies pages, cleans/invalidates destination cache lines to PoC, and loops until `IND_DONE_BIT`. It then drains writes, invalidates I-cache, disables the MMU, and enters the new image either via HVC soft restart when EL2 vectors are provided or directly via `br x28` at EL1.

Dependencies and integration: depends on kexec data structures, page-copy assembler macros, cache maintenance helpers, MMU disable workarounds, virtualization state, and the machine_kexec setup code that supplies safe memory and populated `kimage` fields.

Risks: this code runs while destroying the old kernel memory map; all state must be in registers or safe copied text/data. Cache, TLB, and MMU ordering errors can boot a corrupted new kernel. EL2 versus EL1 entry register conventions must match the receiving image.

Test signals: kexec/kdump boot tests with and without EL2, varied memory layouts, and cache-coherency stress. Failures show as hangs after kexec, bad DTB handoff, or new kernel decompression/entry crashes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/relocate_kernel.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/return_address.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kernel/return_address.c

Purpose: this file implements the generic `return_address()` helper for ARM64 using the architecture stack unwinder.

Important APIs and state: `struct return_address_data` carries a target frame level and output address. `save_return_addr()` is the stack-walk callback and is marked `NOKPROBE_SYMBOL`. `return_address()` is exported GPL and also marked not probeable.

Control flow: `return_address(level)` adds 2 to the requested level to skip its own frames, initializes the result to NULL, and calls `arch_stack_walk()` over the current task. The callback decrements the level for each PC; when the target level is reached, it stores the PC and stops the walk. If the walk ended before the requested level, NULL is returned.

Dependencies and integration: depends on ARM64 stacktrace unwinding and ftrace users that call `return_address()`. The NOKPROBE annotations prevent recursive instrumentation of unwinder-sensitive code.

Risks: returned PCs depend on frame-pointer/unwind reliability, compiler instrumentation, and skipped frame count. It should not be used as a security boundary. Probing it would risk recursion through stack walking.

Test signals: ftrace users, stacktrace tests, and callers expecting NULL for excessive levels. Bad behavior appears as incorrect caller addresses or unwinder recursion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/return_address.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/rsi.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kernel/rsi.c

Purpose: this file initializes Realm Management Extension RSI support for ARM Confidential Compute Realms. It detects RSI availability, configures memory encryption attributes, marks RAM protected, registers ioremap behavior, and creates a dummy platform device for RSI consumers.

Important APIs and state: `config` stores `realm_config`. `prot_ns_shared` is exported and encodes the non-secure shared PTE bit derived from IPA width. `rsi_present` is an exported static key. `cc_platform_has()` reports `CC_ATTR_MEM_ENCRYPT` in Realm world. `arm64_rsi_is_protected()` checks RIPAS state for a physical range. `arm64_rsi_init()` performs early initialization. `arm64_create_dummy_rsi_dev()` registers `RSI_PDEV_NAME` at arch init time.

Control flow: initialization requires SMC conduit, a matching RSI version, successful realm config query, successful ioremap hook registration, and memory encryption ops registration. It then iterates memblock memory and calls `rsi_set_memory_range_protected_safe()` for each range, panicking if any conversion fails, and enables the static key. The ioremap hook chooses encrypted attributes for protected/trusted ranges and decrypted attributes for empty/shared ranges.

Dependencies and integration: depends on SMCCC/PSCI conduit setup, memblock, SWIOTLB/memory encryption abstractions, ARM64 ioremap protection hooks, RSI SMC wrappers, and platform bus registration.

Risks: memory protection setup is irreversible enough that failures panic early to avoid later synchronous external aborts. Range protection checks align to RSI granules and must handle overflow. Incorrect encrypted/decrypted mapping selection can break device or shared-memory access.

Test signals: Realm boot logs showing RSI version, enabled `rsi_present`, successful protected memory conversion, ioremap behavior for trusted versus shared MMIO, and platform device creation. Failures appear as early panic or SEA on memory access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/rsi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/sdei.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kernel/sdei.c

Purpose: this file provides ARM64 architecture support for Software Delegated Exception Interface events. It allocates per-CPU SDEI stacks and optional shadow call stacks, selects the firmware entry point, and handles SDEI event return routing.

Important APIs and state: globals include `sdei_exit_mode`, per-CPU normal/critical SDEI stack pointers, optional per-CPU normal/critical SCS pointers, and per-CPU active event pointers. `sdei_arch_get_entry_point()` returns the handler/trampoline address firmware should call. `do_sdei_event()` reconstructs clobbered registers, calls the generic SDEI event handler, and returns a firmware action code or exception-vector address.

Control flow: stack allocation loops over possible CPUs and unwinds on failure. SCS allocation is skipped when SCS is disabled. Entry-point selection rejects nVHE configurations, records whether exit uses HVC or SMC, and returns a trampoline alias when KPTI/unmapped-at-EL0 requires it. Event handling retrieves missing register values via `sdei_api_event_context()`, calls `sdei_event_handler()`, warns if the handler took a synchronous exception, then either returns handled for masked kernel contexts or redirects to the normal IRQ vector for kernel, AArch32 user, or AArch64 user return paths.

Dependencies and integration: depends on ARM SDEI core, SMCCC conduit, VMAP stacks, SCS allocator, exception vector layout, KPTI trampoline aliases, ptrace regs, and stacktrace/kprobe annotations.

Risks: SDEI may interrupt contexts where the normal stack is unsafe, hence dedicated stacks. Entry support is unavailable in nVHE boot state. Incorrect return vector choice can skip signal/KVM handling or return to unsafe interrupted context. Stack/SCS allocation failures disable SDEI by returning zero entry point.

Test signals: firmware SDEI probe, normal and critical event delivery, KPTI trampoline entry, SCS-enabled builds, and signal delivery after user-mode SDEI interruption. Warnings about exceptions during handlers are high-risk diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/sdei.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/setup.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kernel/setup.c

Purpose: this is the main ARM64 architecture setup file. It records boot CPU identity, validates and maps the FDT, initializes early memory and firmware paths, builds CPU MPIDR mapping helpers, registers memory resources, and installs panic/boot sanity hooks.

Important APIs and state: globals include `__fdt_pointer`, `mmu_enabled_at_boot`, `boot_args[4]`, `mpidr_hash`, `__cpu_logical_map`, `standard_resources`, and kernel code/data resources. Public functions include `smp_setup_processor_id()`, `arch_match_cpu_phys_id()`, `cpu_logical_map()`, `setup_arch()`, and `arch_cpu_is_hotpluggable()`.

Control flow: `setup_arch()` initializes `init_mm`, command line, KASLR, fixmap/ioremap, FDT scanning, jump labels, early params, dynamic SCS, DAIF state, idmap teardown, Xen/EFI, memblock, paging, ACPI/DT, bootmem, KASAN, standard resources, PSCI, RSI, CPU ops, SMP CPU enumeration, MPIDR hash, SW TTBR0 PAN state, and boot-argument warnings. `setup_machine_fdt()` remaps the FDT, reserves it, scans it, remaps read-only, and records machine description. Resource setup registers System RAM/reserved regions and later splits reserved ranges.

Dependencies and integration: central integration point for firmware discovery (FDT/ACPI/EFI/PSCI/RSI/Xen), memory management, SMP, CPU feature/static-key setup, dynamic SCS, KASAN, panic notifiers, and boot protocol validation.

Risks: ordering is critical: FDT and early params precede memory and CPU feature decisions; DAIF unmasking occurs only after early console readiness; idmap removal prevents speculative TTBR0 use. Broken bootloaders are warned for nonzero x1-x3 and can panic if booted non-EFI with MMU/caches enabled.

Test signals: boot logs for CPU ID, machine model, KASLR offset, boot-arg warnings, PSCI/ACPI selection, resource layout in `/proc/iomem`, CPU hotplug eligibility, and panic notifier output. Device-tree alignment/size errors halt very early.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/setup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/signal.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kernel/signal.c

Purpose: this file implements native AArch64 signal delivery and `rt_sigreturn`. It builds and parses extensible user signal frames containing GPRs, sigmask, altstack, FPSIMD, ESR, SVE/SME, TPIDR2, ZA/ ZT, FPMR, POE, and GCS contexts, and coordinates syscall restart behavior.

Important APIs and state: key structures are `rt_sigframe`, `rt_sigframe_user_layout`, `user_access_state`, and `user_ctxs`. Public entry points include `SYSCALL_DEFINE0(rt_sigreturn)`, `arch_do_signal_or_restart()`, and `minsigstksz_setup()`. Important helpers include `setup_sigframe_layout()`, `setup_sigframe()`, `get_sigframe()`, `setup_return()`, `setup_rt_frame()`, `parse_user_sigframe()`, `restore_sigframe()`, and per-feature preserve/restore helpers.

Control flow: delivery saves/flushed FP state, computes a 16-byte-aligned frame and optional record layout, temporarily resets POE restrictions so kernel uaccess can build the frame, writes user context records, optionally copies siginfo, pushes GCS signal tokens, then updates pt_regs to enter the handler with correct arguments, SP, FP/LR, PC, BTI BTYPE, TCO clear, and SME streaming/ZA disabled. Return validates SP alignment and access, restores sigmask and GPRs, parses the context chain including `extra_context`, restores feature state in dependency order, validates GCS signal cap token, restores altstack and user-access state, and returns the restored x0.

State and persistence: signal frames persist in user memory and are ABI. The kernel also updates current task FP/SVE/SME/GCS/POE/FPMR/TLS state. `signal_minsigstksz` is computed from the largest supported frame layout after cpufeatures are known.

Dependencies and integration: integrates with generic signal, compat signal32, rseq, syscall restart, ptrace register validation, VDSO sigtramp, FPSIMD/SVE/SME, GCS, POE/pkeys, BTI, MTE TCO, and altstack handling.

Risks: signal frames are security-sensitive user input on sigreturn; duplicate/unknown/misaligned records are rejected. Feature restore order matters, e.g. ZA before ZT and GCS cap validation after context restore. Once `setup_return()` mutates registers, later failures must be avoided. Frame growth is capped by `SIGFRAME_MAXSZ`.

Test signals: signal ABI selftests for SVE/SME/ZA/ ZT/FPMR/POE/GCS, invalid sigreturn frames, altstack, syscall restart, single-step into handlers, BTI-protected handlers, and `AT_MINSIGSTKSZ` sizing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/signal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/signal32.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kernel/signal32.c

Purpose: this file implements AArch32 compatibility signal delivery and `sigreturn`/`rt_sigreturn` for ARM64 kernels running compat tasks. It translates between AArch32 signal frame ABI and ARM64 internal pt_regs/FPSIMD state.

Important APIs and state: structures include `compat_vfp_sigframe` and `compat_aux_sigframe`. Public compat entry points are `COMPAT_SYSCALL_DEFINE0(sigreturn)`, `COMPAT_SYSCALL_DEFINE0(rt_sigreturn)`, `compat_setup_rt_frame()`, `compat_setup_frame()`, and `compat_setup_restart_syscall()`. Helpers convert sigsets, save/restore VFP state, compute compat frame addresses, set return trampolines, and write compat sigcontexts.

Control flow: signal delivery selects old or RT frame shape, places it on an 8-byte-aligned compat stack, writes GPRs, CPSR, fault metadata, sigmask, optional VFP auxiliary state, siginfo/altstack for RT signals, and then updates regs for handler entry. `compat_setup_return()` chooses a user restorer or the kernel-provided compat sigpage stub, handles ARM versus Thumb handler bit, clears IT state, restores endianness, and sets r0/SP/LR/PC/PSTATE. Sigreturn validates SP alignment and access, restores sigmask, GPRs, CPSR via `compat_psr_to_pstate()`, validates user regs, restores VFP if supported, and returns r0.

State and dependencies: uses `thread.uw.fpsimd_state`, current fault address/code, compat VDSO/sigpage, `valid_user_regs()`, altstack helpers, and `__NR_compat32_restart_syscall`. Big-endian builds swap D-register halves out of Q-register storage via `union __fpsimd_vreg`.

Risks: compat signal ABI is fixed and offset-sensitive; the file ends with static assertions for `compat_siginfo_t`. VFP save/restore must handle AArch32 D-register layout despite ARM64 FPSIMD Q-register storage. Restorer selection must encode ARM/Thumb correctly because no OABI userspace is supported.

Test signals: compat signal selftests, Thumb and ARM handlers, old and RT signal frames, VFP state preservation, altstack restore, syscall restart via r7, and static assert build failures if ABI layouts drift.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/signal32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/sigreturn32.S -->
# sources/distributed-fs/ceph-client/arch/arm64/kernel/sigreturn32.S

Purpose: this assembly file provides the AArch32 signal-return code blob copied or mapped for compat tasks. It contains ARM and Thumb instruction sequences for `sigreturn` and `rt_sigreturn`.

Important symbols: `__aarch32_sigret_code_start` and `__aarch32_sigret_code_end` bracket the `.rodata` byte sequence. The sequence includes four variants: ARM `sigreturn`, Thumb `sigreturn`, ARM `rt_sigreturn`, and Thumb `rt_sigreturn`.

Control flow: for ARM state, bytes encode `mov r7, #__NR_compat32_sigreturn` or `#__NR_compat32_rt_sigreturn` followed by `svc`. For Thumb state, two 16-bit instructions load r7 and execute SVC with the corresponding syscall number. `signal32.c` selects the right offset based on `SA_SIGINFO` and handler Thumb bit when no user restorer is supplied.

Dependencies and integration: depends on `asm/unistd_compat_32.h` syscall numbers and the compat signal page setup. It intentionally does not support OABI userspace, matching the C-side comments.

Risks: byte ordering and offsets are ABI-visible; changing the order breaks `compat_setup_return()` indexing. The code must remain in read-only data and be copied/mapped exactly for compat userspace.

Test signals: compat signal return from ARM and Thumb handlers, RT and non-RT signals, and disassembly of the sigpage. Failures appear as bad syscall numbers in r7 or SIGILL/SIGSEGV when returning from compat handlers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/sigreturn32.S -->
