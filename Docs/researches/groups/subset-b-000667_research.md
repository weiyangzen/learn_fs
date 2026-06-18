# subset-b-000667 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/probes/uprobes/Makefile -->
## sources/distributed-fs/ceph-client/arch/arm/probes/uprobes/Makefile

### Purpose
Builds the ARM uprobes implementation when `CONFIG_UPROBES` is enabled by adding `core.o` and `actions-arm.o`.

### Important APIs, Types, And Functions
The only build API is `obj-$(CONFIG_UPROBES) += core.o actions-arm.o`, which binds generic uprobe support to ARM instruction analysis and action handling.

### Control Flow
Kbuild evaluates the config symbol, then compiles and links the two objects into the ARM architecture build. There is no runtime control flow in this file.

### State, Persistence, And Dependencies
State is build metadata only. It depends on Kbuild config selection and on both C files compiling against ARM probe decoding and generic uprobe headers.

### Integration Points
Integrates `arch/arm/probes/uprobes` into the kernel image so generic uprobes can trap, single-step, and emulate ARM user instructions.

### Risks
If the object list drifts from source exports, ARM uprobes may link without required decoders or fail at build time. Config-only coverage means disabled builds hide errors.

### Test Signals
Build ARM kernels with `CONFIG_UPROBES=y`, run uprobe/kprobe selftests on ARM, and verify both object files appear in build logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/probes/uprobes/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/probes/uprobes/actions-arm.c -->
## sources/distributed-fs/ceph-client/arch/arm/probes/uprobes/actions-arm.c

### Purpose
Implements ARM-specific uprobe decode actions for instructions that need PC substitution, writeback handling, branch simulation, or rejection before execution out of line.

### Important APIs, Types, And Functions
Key helpers are `uprobes_substitute_pc`, `uprobe_set_pc`, `uprobe_unset_pc`, `uprobe_aluwrite_pc`, `uprobe_write_pc`, `decode_pc_ro`, `decode_wb_pc`, `decode_rd12rn16rm0rs8_rwflags`, `decode_ldr`, and `uprobe_decode_ldmstm`. The exported action table is `uprobes_probes_actions[]`, mapping `PROBES_*` decode classes to simulation handlers or per-class decoders.

### Control Flow
The generic ARM probe decoder classifies an instruction and indexes `uprobes_probes_actions[]`. PC-relative instructions are rewritten in the copied XOL instruction to use a free general register; prehandlers seed that register with `ARM_pc + 8`; posthandlers restore it or route writes through `alu_write_pc`/`load_write_pc`. LDM/STM with PC in the register list is either rejected or rewritten to use LR so the posthandler can apply branch semantics.

### State, Persistence, And Dependencies
Persistent per-probe state lives in `struct arch_uprobe`: `ixol`, `pcreg`, `prehandler`, and `posthandler`. Per-task temporary state uses `struct arch_uprobe_task.backup`. Dependencies include `decode-arm.h`, `core.h`, generic `linux/uprobes.h`, ARM opcode conversion helpers, and probe simulation functions such as `simulate_bbl`.

### Integration Points
Called by `arch_uprobe_analyze_insn()` in `core.c`; its action table is the ARM uprobe policy for what can be simulated, executed in XOL, or rejected. It also integrates with ARM PC write semantics through `alu_write_pc` and `load_write_pc`.

### Risks
Incorrect free-register selection corrupts user registers. PC bias must remain ARM-state `+8`; Thumb is not supported here. LDM/STM rewriting must reject LR conflicts, or return-path behavior can be corrupted.

### Test Signals
Exercise uprobes on PC-relative loads/stores, ALU writes to PC, branches, and LDM/STM forms. Verify rejected instructions return `-EINVAL` and successful probes preserve user register state and branch destinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/probes/uprobes/actions-arm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/probes/uprobes/core.c -->
## sources/distributed-fs/ceph-client/arch/arm/probes/uprobes/core.c

### Purpose
Provides the ARM architecture glue for generic uprobes: breakpoint opcode installation, instruction analysis, XOL copy/pre/post handling, return-probe LR hijacking, and undefined-instruction trap registration.

### Important APIs, Types, And Functions
Important entry points include `is_swbp_insn`, `set_swbp`, `arch_uprobe_ignore`, `arch_uprobe_skip_sstep`, `arch_uretprobe_hijack_return_addr`, `arch_uprobe_analyze_insn`, `arch_uprobe_copy_ixol`, `arch_uprobe_pre_xol`, `arch_uprobe_post_xol`, `arch_uprobe_xol_was_trapped`, `arch_uprobe_abort_xol`, `uprobe_get_swbp_addr`, and `arch_uprobes_init`.

### Control Flow
Analysis rejects unaligned/Thumb addresses, decodes the ARM instruction, prepares one copied instruction plus an ARM single-step trap, and derives a condition-coded software breakpoint. At trap time `uprobe_trap_handler()` distinguishes breakpoint and single-step opcodes, then calls generic pre/post single-step notifiers with local IRQs disabled. XOL setup saves the previous thread trap number, marks it as `UPROBE_TRAP_NR`, and redirects `ARM_pc`; post-XOL restores the trap number and advances to the original instruction plus four bytes.

### State, Persistence, And Dependencies
Per-probe state includes `bpinsn`, `ixol`, `simulate`, and decoded `asi` handlers. Per-task state uses `current->utask`, `autask.saved_trap_no`, and the XOL/original virtual addresses. Dependencies include undefined-instruction hooks, highmem mapping, cache flush via `flush_uprobe_xol_access`, and generic uprobe notifier paths.

### Integration Points
Registers `undef_hook` entries at `device_initcall`, making ARM undefined-instruction traps the uprobe breakpoint and single-step mechanism. It interacts with generic return probes by replacing `ARM_lr` with a trampoline address.

### Risks
Unsupported Thumb addresses return `-EINVAL`; mixed ARM/Thumb probe expectations will fail. Trap-number bookkeeping is context-sensitive; bad restore paths can misreport later exceptions. Cache flushing and XOL page mapping must be correct for self-modifying executable code.

### Test Signals
Run uprobes and uretprobes on ARM userspace functions, including conditional instructions and simulated instructions. Fault inside XOL to validate abort/trap detection. Confirm cache coherency on VIPT/noncoherent ARM targets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/probes/uprobes/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/probes/uprobes/core.h -->
## sources/distributed-fs/ceph-client/arch/arm/probes/uprobes/core.h

### Purpose
Declares the ARM uprobe decoder callbacks and shared decode-action table used between `core.c` and `actions-arm.c`.

### Important APIs, Types, And Functions
Exports prototypes for `uprobe_decode_ldmstm`, `decode_ldr`, `decode_rd12rn16rm0rs8_rwflags`, `decode_wb_pc`, `decode_pc_ro`, and `uprobes_probes_actions[]`.

### Control Flow
There is no runtime flow. The header allows the instruction analyzer to pass function pointers to the generic ARM probe decoder and lets action implementations remain in a separate translation unit.

### State, Persistence, And Dependencies
It declares no storage except the external action table. It depends on decode types such as `probes_opcode_t`, `struct arch_probes_insn`, and `struct decode_header` being visible through including C files.

### Integration Points
Acts as the private contract for ARM uprobe code under `arch/arm/probes/uprobes`.

### Risks
Prototype drift breaks build or, worse, mismatches decoder semantics. Since it is private, broad kernel users should not include it.

### Test Signals
Compile with `CONFIG_UPROBES=y` and run sparse/compiler checks to catch prototype or constness mismatches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/probes/uprobes/core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/tools/Makefile -->
## sources/distributed-fs/ceph-client/arch/arm/tools/Makefile

### Purpose
Generates ARM architecture headers and syscall assembly tables used by kernel and UAPI builds.

### Important APIs, Types, And Functions
Build targets include generated `calls-oabi.S`, `calls-eabi.S`, `unistd-nr.h`, `mach-types.h`, `unistd-oabi.h`, and `unistd-eabi.h`. Commands wrap `gen-mach-types`, `scripts/syscallhdr.sh`, `scripts/syscalltbl.sh`, and `syscallnr.sh`.

### Control Flow
`kapi` depends on generated kernel headers and syscall tables; `uapi` depends on generated user ABI headers. Kbuild creates output directories, then invokes AWK or shell scripts through `if_changed` rules so outputs regenerate when inputs or commands change.

### State, Persistence, And Dependencies
State is generated files under `arch/$(ARCH)/include/generated`. Inputs are `mach-types`, `syscall.tbl`, generic syscall scripts, and Kbuild variables such as `ARCH`, `src`, `srctree`, and `CONFIG_SHELL`.

### Integration Points
Feeds ARM syscall numbering, OABI/EABI entry tables, and machine-type helpers into the rest of the ARM build.

### Risks
Generated UAPI header drift is ABI-sensitive. Missing directory creation or stale `if_changed` dependencies can leave obsolete syscall counts or machine IDs in builds.

### Test Signals
Run `make ARCH=arm archprepare`, inspect generated headers, and compare syscall table output after syscall additions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/tools/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/tools/gen-mach-types -->
## sources/distributed-fs/ceph-client/arch/arm/tools/gen-mach-types

### Purpose
AWK generator that converts ARM `mach-types` rows into `include/generated/asm/mach-types.h`.

### Important APIs, Types, And Functions
The script recognizes non-comment rows with either four fields, including a registered numeric machine type, or three fields for unregistered machines. It emits `MACH_TYPE_*` constants and `machine_is_*()` macros.

### Control Flow
During `BEGIN`, it initializes a row count. Each valid line stores generated symbol names, config symbols, and optional numbers. In `END`, it prints the header guard, declares `__machine_arch_type`, emits registered `#define MACH_TYPE_*` values, then emits config-gated `machine_is_*()` predicates and always-false predicates for unregistered machines.

### State, Persistence, And Dependencies
State is AWK arrays accumulated from the input file. The persistent output is a generated C header. It depends on row ordering and field layout in `arch/arm/tools/mach-types`.

### Integration Points
Board and platform code include `mach-types.h` to select legacy machine descriptions and compare the boot machine ID.

### Risks
Malformed rows silently disappear unless they have three or four fields. Name collisions in machine or config names produce broken C macros. Registered numeric IDs are ABI-like bootloader contracts.

### Test Signals
Regenerate `mach-types.h`, compile platform code that uses `machine_is_*()`, and diff output after `mach-types` changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/tools/gen-mach-types -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/tools/syscallnr.sh -->
## sources/distributed-fs/ceph-client/arch/arm/tools/syscallnr.sh

### Purpose
Generates an ARM `unistd-nr.h`-style header containing an aligned `__NR_syscalls` value derived from the highest syscall number.

### Important APIs, Types, And Functions
Inputs are the syscall table path and output header path. The script computes a file guard from the output basename and emits `#define __NR_syscalls`.

### Control Flow
It filters numeric syscall rows, sorts them, takes the highest entry, increments the number, grows the alignment from 1 by factors of 4 while crossing 256-aligned ranges, rounds up, and writes the guarded header.

### State, Persistence, And Dependencies
State is local shell variables `in`, `out`, `align`, and `fileguard`. It depends on POSIX shell, `grep`, `sort`, `tail`, `basename`, and `sed`.

### Integration Points
Called by `arch/arm/tools/Makefile` when generating kernel syscall API headers.

### Risks
Assumes syscall numbers sort correctly with `sort -n`; unusual hexadecimal formats must remain accepted by shell arithmetic. If the last row is malformed, syscall count generation becomes wrong.

### Test Signals
Add a high syscall number to a temporary table and confirm the generated count rounds as expected. Run shellcheck-style review and `make ARCH=arm archprepare`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/tools/syscallnr.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/vdso/Makefile -->
## sources/distributed-fs/ceph-client/arch/arm/vdso/Makefile

### Purpose
Builds the ARM 32-bit vDSO shared object, validates it, munges ELF flags for ABI compatibility, strips the runtime `.so`, and embeds it into `vdso.o`.

### Important APIs, Types, And Functions
Defines host program `vdsomunge`, vDSO objects `vgettimeofday.o` and `note.o`, targets `vdso.so`, `vdso.so.dbg`, `vdso.so.raw`, and `vdso.lds`, and commands `vdsold_and_vdso_check` and `vdsomunge`.

### Control Flow
Kbuild preprocesses the linker script, compiles PIC vDSO objects with branch profiling disabled, links `vdso.so.raw`, runs generic vDSO checks, runs `vdsomunge` to clear soft-float ABI flags, strips debug symbols for `vdso.so`, and ensures `vdso.o` depends on the final shared object.

### State, Persistence, And Dependencies
Build artifacts persist under the object directory. Dependencies include `lib/vdso/Makefile.include`, host compiler support, linker flags, `c-gettimeofday-y`, and config-controlled endianness.

### Integration Points
The generated `vdso.so` is included by `vdso.S` and later mapped into userspace by ARM kernel vDSO setup.

### Risks
Wrong C flags can introduce libgcc, stack protector, profiling, or randomization dependencies unsuitable for vDSO. ABI flags must be compatible with both soft- and hard-float userspace. Linker script and check command failures are runtime ABI risks.

### Test Signals
Build with `CONFIG_VDSO=y` for little and BE8 configurations, run `readelf -h/-l/-s`, and execute gettimeofday/clock_gettime vDSO tests under ARM userspace.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/vdso/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/vdso/note.c -->
## sources/distributed-fs/ceph-client/arch/arm/vdso/note.c

### Purpose
Adds ELF note metadata and build salt to the ARM vDSO image.

### Important APIs, Types, And Functions
Uses `ELFNOTE32("Linux", 0, LINUX_VERSION_CODE)` and `BUILD_SALT`.

### Control Flow
There is no runtime logic. The compiler emits note sections that the vDSO linker script places into the PT_NOTE segment.

### State, Persistence, And Dependencies
Persistent state is embedded ELF note data. Dependencies include `linux/version.h`, `linux/elfnote.h`, and `linux/build-salt.h`.

### Integration Points
The note is linked with vDSO text and visible to userspace ELF tooling and debuggers.

### Risks
Incorrect note section format can break vDSO validation or confuse consumers that inspect vDSO metadata.

### Test Signals
Run `readelf -n` on `vdso.so.dbg` and confirm Linux version and build salt notes are present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/vdso/note.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/vdso/vdso.S -->
## sources/distributed-fs/ceph-client/arch/arm/vdso/vdso.S

### Purpose
Embeds the built ARM `vdso.so` binary into a page-aligned, read-only-after-init kernel data range.

### Important APIs, Types, And Functions
Defines global symbols `vdso_start` and `vdso_end` around `.incbin "arch/arm/vdso/vdso.so"`.

### Control Flow
Assembly switches to `.data..ro_after_init`, aligns to `PAGE_SIZE`, includes the binary vDSO, aligns again, and returns to the previous section.

### State, Persistence, And Dependencies
State is the embedded vDSO image in kernel memory. It depends on `vdso.so` existing before assembly and on page-size constants from `asm/page.h`.

### Integration Points
Kernel vDSO mapping code uses `vdso_start`/`vdso_end` to copy or map the image into user address spaces.

### Risks
Misalignment or missing dependency on `vdso.so` can produce invalid mappings. Embedding the wrong path silently packages a stale or absent vDSO.

### Test Signals
Inspect `nm vmlinux` for `vdso_start`/`vdso_end`, confirm size matches `vdso.so`, and boot-test userspace vDSO calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/vdso/vdso.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/vdso/vdso.lds.S -->
## sources/distributed-fs/ceph-client/arch/arm/vdso/vdso.lds.S

### Purpose
ARM vDSO linker script defining ELF format, sections, program headers, discarded data, and the public `LINUX_2.6` symbol version.

### Important APIs, Types, And Functions
Exports versioned symbols `__vdso_clock_gettime`, `__vdso_gettimeofday`, `__vdso_clock_getres`, `__vdso_clock_gettime64`, and `__vdso_clock_getres_time64`. It also expands `VDSO_VVAR_SYMS`.

### Control Flow
The linker lays out headers, dynamic symbol sections, notes, unwind metadata, dynamic data, rodata, executable text, GOT/relocation sections, and discards writable/bss sections. Program headers force one read-execute PT_LOAD plus PT_DYNAMIC, PT_NOTE, and EH frame headers.

### State, Persistence, And Dependencies
State is ELF layout metadata. Dependencies include `asm/vdso.h`, `vdso/datapage.h`, ARM ELF output formats, and vDSO object section names.

### Integration Points
Controls the ABI exposed to user loaders and libc. The exported version block is the contract by which user programs resolve vDSO functions.

### Risks
Writable sections are discarded intentionally; any vDSO C change needing writable storage will fail or mislink. Wrong program headers can make the image unmappable or fail generic vDSO checks.

### Test Signals
Run `readelf -l -S --version-info` on `vdso.so.dbg`, verify one PT_LOAD and expected global symbols, and run clock/gettimeofday ABI tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/vdso/vdso.lds.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/vdso/vdsomunge.c -->
## sources/distributed-fs/ceph-client/arch/arm/vdso/vdsomunge.c

### Purpose
Host build utility that copies an ARM vDSO shared object while clearing `EF_ARM_ABI_FLOAT_SOFT` and rejecting hard-float or unsupported ELF inputs.

### Important APIs, Types, And Functions
Key functions are `fail`, `cleanup`, `read_elf_word`, `read_elf_half`, `write_elf_word`, and `main`. It uses ELF32 headers, `mmap`, `ftruncate`, `msync`, and ARM `e_flags` constants.

### Control Flow
`main` validates arguments, maps the input ELF, checks magic, class, data order, `ET_DYN`, `EM_ARM`, and EABI v5. It fails if hard-float is set, copies the input to a writable output mapping, clears the soft-float flag if present, syncs, and lets `cleanup()` remove the output on failure.

### State, Persistence, And Dependencies
Persistent state is the output `.so.dbg`. Local state includes endian-swap decisions and the global failure/outfile variables used by `atexit`. Dependencies are host libc, `<elf.h>`, and kernel-defined fallback constants for older host headers.

### Integration Points
Invoked by the ARM vDSO Makefile between raw linking and stripping so the final vDSO is usable by both soft- and hard-float programs that do not pass FP arguments.

### Risks
Insufficient ELF validation could map short files and read invalid headers. Any future vDSO FP argument/result would invalidate the flag-clearing assumption. Host endianness and target ELF data order must be handled correctly.

### Test Signals
Run on sample ARM ELF files with soft, hard, and no float flags; check output `e_flags` with `readelf -h`; verify failure removes partial output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/vdso/vdsomunge.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/vdso/vgettimeofday.c -->
## sources/distributed-fs/ceph-client/arch/arm/vdso/vgettimeofday.c

### Purpose
Implements the ARM userspace vDSO wrappers for clock and time queries using generic common-vDSO helpers.

### Important APIs, Types, And Functions
Exports `__vdso_clock_gettime`, `__vdso_clock_gettime64`, `__vdso_gettimeofday`, `__vdso_clock_getres`, and `__vdso_clock_getres_time64`. It also defines empty `__aeabi_unwind_cpp_pr0/pr1/pr2` symbols to satisfy compiler-emitted unwind references.

### Control Flow
Each vDSO function directly forwards to the corresponding `__cvdso_*` helper, preserving 32-bit or 64-bit time ABI types. The unwind stubs return immediately.

### State, Persistence, And Dependencies
No writable state is allowed. Runtime data comes from the vDSO/vvar datapage read by generic helpers. Dependencies include `vdso/gettime.h`, `asm/vdso.h`, and old/new kernel time structures.

### Integration Points
Linked and versioned by `vdso.lds.S`; libc resolves these symbols for low-overhead time queries without syscalls when clocks are supported.

### Risks
Type mismatch between old 32-bit and time64 structures can corrupt userspace outputs. Unexpected compiler runtime references are dangerous in vDSO, hence the local unwind stubs.

### Test Signals
Run vDSO clock/gettimeofday selftests, compare against syscall fallback, and inspect dynamic symbols for unresolved references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/vdso/vgettimeofday.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/vfp/Makefile -->
## sources/distributed-fs/ceph-client/arch/arm/vfp/Makefile

### Purpose
Builds the ARM VFP support objects: module glue, hardware register save/restore assembly, and software single/double emulation.

### Important APIs, Types, And Functions
Adds `vfpmodule.o`, `vfphw.o`, `vfpsingle.o`, and `vfpdouble.o` to `obj-y`. Debug flags are present but commented.

### Control Flow
Kbuild compiles all four objects whenever this directory is selected by the ARM architecture configuration.

### State, Persistence, And Dependencies
State is build metadata. Runtime state lives in the compiled objects, especially per-thread VFP state and exception handlers.

### Integration Points
Links VFP context management, undefined-instruction hooks, and emulators into the ARM kernel.

### Risks
Omitting any object breaks either hardware access helpers or emulation entry points. Debug flag changes can affect timing and code generation in exception paths.

### Test Signals
Build ARM VFP-enabled and VFP-disabled configurations; run floating point context-switch, signal, and exception tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/vfp/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/vfp/vfp.h -->
## sources/distributed-fs/ceph-client/arch/arm/vfp/vfp.h

### Purpose
Private VFP arithmetic and state header defining unpacked single/double formats, normalization helpers, exception constants, operation descriptors, and hardware state entry points.

### Important APIs, Types, And Functions
Defines `struct vfp_single`, `struct vfp_double`, `struct op`, `VFP_*` type/exception constants, packing/unpacking helpers, 64/128-bit arithmetic helpers, `vfp_estimate_div128to64`, `vfp_estimate_sqrt_significand`, normalise/round prototypes, register access prototypes, and `vfp_save_state`/`vfp_load_state`.

### Control Flow
Most code is inline arithmetic used by `vfpsingle.c` and `vfpdouble.c`: unpack packed IEEE values, classify zeros/denormals/infinities/NaNs, perform jamming shifts and wide arithmetic, then repack after rounding. Assembly-backed prototypes bridge C emulation to hardware VFP registers.

### State, Persistence, And Dependencies
State is passed through unpacked structs and per-thread VFP hard state. It depends on ARM inline assembly constraints, `do_div`, VFP register numbering, and config-dependent `VFP_REG_ZERO`.

### Integration Points
Shared by VFP module, hardware assembly, and both precision emulators. It is central to preserving IEEE-754 semantics when hardware bounces instructions for software completion.

### Risks
Rounding and jamming helpers are precision-critical; off-by-one errors create silent FP miscomputations. Register numbering differs with `CONFIG_VFPv3`, so compare-with-zero paths must match hardware capabilities.

### Test Signals
Run IEEE single/double conformance vectors, denormal/NaN/overflow tests, and build both VFPv2 and VFPv3 configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/vfp/vfp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/vfp/vfpdouble.c -->
## sources/distributed-fs/ceph-client/arch/arm/vfp/vfpdouble.c

### Purpose
Implements software emulation for ARM VFP double-precision instructions, including arithmetic, comparisons, conversions, NaN handling, and dispatch from decoded opcodes.

### Important APIs, Types, And Functions
Key functions include `vfp_double_normaliseround`, `vfp_double_fsqrt`, `vfp_compare`, `vfp_double_fcvts`, integer conversion helpers, multiply/add/divide helpers, `vfp_double_multiply`, `vfp_double_add`, `vfp_double_multiply_accumulate`, and exported dispatcher `vfp_double_cpdo`. Dispatch tables `fops_ext[]` and `fops[]` map instruction fields to operations.

### Control Flow
`vfp_double_cpdo()` decodes destination/source registers and opcode class, fetches operands with `vfp_get_double`, and calls the relevant operation. Operations unpack operands, classify special values, handle NaNs and exceptions, perform integer/significand arithmetic, normalize and round, write results through `vfp_put_double` or conversion stores, and return FPSCR exception bits.

### State, Persistence, And Dependencies
Uses transient `struct vfp_double` values and hardware VFP register accessors from `vfphw.S`. Persistent state is FPSCR flags and per-thread saved registers managed by `vfpmodule.c`. It depends on helper math in `vfp.h` and instruction field macros in `vfpinstr.h`.

### Integration Points
Called by `vfp_emulate_instruction()` when a bounced CPDO double instruction requires software handling. It shares sqrt estimate logic with single precision and returns exception masks to `vfp_raise_exceptions`.

### Risks
IEEE corner cases are dense: signaling NaNs, signed zero, denormals, inexact, overflow, underflow, and conversion saturation all need exact FPSCR behavior. Division and sqrt iterative estimates are sensitive to normalization invariants.

### Test Signals
Run double-precision FP conformance suites, NaN propagation tests, conversion boundary tests, and perf/software-emulation counters for bounced instructions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/vfp/vfpdouble.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/vfp/vfphw.S -->
## sources/distributed-fs/ceph-client/arch/arm/vfp/vfphw.S

### Purpose
Provides assembly routines to save/load VFP hardware state and to read/write individual single and double VFP registers.

### Important APIs, Types, And Functions
Exports `vfp_load_state`, `vfp_save_state`, `vfp_get_float`, `vfp_put_float`, `vfp_get_double`, and `vfp_put_double`. Uses VFP macros such as `VFPFLDMIA`, `VFPFSTMIA`, `VFPFMRX`, and `VFPFMXR`.

### Control Flow
State load restores VFP working registers, then FPEXC/FPSCR/FPINST/FPINST2 as required by exception bits. Save stores working registers and exception/status registers. Register accessors use table branches to fixed-size snippets that move specific `sN` or `dN` registers to/from ARM core registers; VFPv3 conditionally includes `d16`-`d31`.

### State, Persistence, And Dependencies
Persistent state is stored in per-thread VFP hard-state memory. The routines depend on exact struct offsets, VFP assembler support, and `CONFIG_VFPv3` register availability.

### Integration Points
Called from `vfpmodule.c` for context switching and from emulators to fetch/store operands.

### Risks
Assembler table layout must remain exact; bad `.org` spacing or Thumb2 branch handling reads the wrong register. Saving FPINST2 only when valid must mirror hardware FPEXC semantics.

### Test Signals
Context-switch tests that fill all VFP registers, signal save/restore tests, VFPv2 vs VFPv3 builds, and disassembly review of table branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/vfp/vfphw.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/vfp/vfpinstr.h -->
## sources/distributed-fs/ceph-client/arch/arm/vfp/vfpinstr.h

### Purpose
Defines VFP instruction decoding masks, register extraction macros, FPSCR condition flags, and inline accessors for VFP system registers.

### Important APIs, Types, And Functions
Macros include `INST_CPRTDO`, `INST_CPRT`, `FOP_*`, `FEXT_*`, `vfp_get_sd/dd/sm/dm/sn/dn`, `vfp_single`, `FPSCR_N/Z/C/V`, `fmrx`, and `fmxr`. It declares `vfp_single_cpdo`, `vfp_single_cprt`, and `vfp_double_cpdo`.

### Control Flow
Consumers mask opcode fields to decide CPDO/CPRT class, precision, operation index, and register numbers. `fmrx`/`fmxr` emit VFP system-register transfer instructions.

### State, Persistence, And Dependencies
No storage is declared. It depends on ARM VFP instruction encoding and compiler support for inline assembly with `.fpu vfpv2`.

### Integration Points
Shared by VFP exception entry and the single/double emulators; it is the decode vocabulary for bounced VFP instructions.

### Risks
Incorrect bit masks route instructions to wrong emulation handlers or wrong registers. Inline system register access is privileged/context-sensitive and must only run when VFP access is enabled.

### Test Signals
Decode known instruction encodings, run CPDO/CPRT emulation tests, and build with GCC/Clang assemblers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/vfp/vfpinstr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/vfp/vfpmodule.c -->
## sources/distributed-fs/ceph-client/arch/arm/vfp/vfpmodule.c

### Purpose
Owns ARM VFP runtime support: detection, lazy context switching, undefined-instruction exception handling, software bounce/emulation, signal-frame save/restore, CPU hotplug/PM, and kernel NEON entry.

### Important APIs, Types, And Functions
Important functions include `vfp_state_hold/release`, `vfp_force_reload`, `vfp_thread_flush/exit/copy`, `vfp_notifier`, `vfp_raise_exceptions`, `vfp_emulate_instruction`, `VFP_bounce`, `vfp_enable`, `vfp_disable`, `vfp_sync_hwstate`, `vfp_flush_hwstate`, `vfp_preserve_user_clear_hwstate`, `vfp_restore_user_hwstate`, `vfp_support_entry`, `kernel_neon_begin/end`, `vfp_detect`, and `vfp_init`.

### Control Flow
At boot `vfp_init()` enables access, probes FPSID, discovers VFP/NEON features, registers undefined-instruction hooks, thread notifiers, CPU hotplug callbacks, and PM callbacks. At runtime an undefined VFP/NEON instruction enters `vfp_support_entry()`, lazily loads the current task state if needed, retries if no exception is pending, or calls `VFP_bounce()` to emulate the faulting FP instruction(s) and raise SIGFPE when FPSCR enables trapped exceptions.

### State, Persistence, And Dependencies
Global state includes `have_vfp`, `VFP_arch`, `vfp_current_hw_state[NR_CPUS]`, ELF hwcaps, and undefined hooks. Per-thread persistent state is `thread_info.vfpstate`. Dependencies include ARM coprocessor access control, thread notifier API, CPU PM/hotplug, perf software events, signal delivery, and `vfphw.S` save/load routines.

### Integration Points
Integrates with scheduler context switches, signal handling, kernel NEON users, CPU feature exposure to userspace, and undefined-instruction traps.

### Risks
Lazy context switching is highly concurrency-sensitive, especially SMP migration and PREEMPT_RT behavior. Kernel-mode FP misuse is fatal. Incorrect FPSCR/FPEXC bounce handling can either lose exceptions or loop on the same instruction.

### Test Signals
Run FP context-switch stress across CPUs, signal save/restore tests, CPU hotplug and suspend/resume tests, NEON kernel selftests, SIGFPE trap tests, and userspace hwcap validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/vfp/vfpmodule.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/vfp/vfpsingle.c -->
## sources/distributed-fs/ceph-client/arch/arm/vfp/vfpsingle.c

### Purpose
Implements software emulation for ARM VFP single-precision instructions, including arithmetic, comparisons, conversions, square root, NaN handling, and opcode dispatch.

### Important APIs, Types, And Functions
Key functions include `vfp_single_normaliseround`, `vfp_estimate_sqrt_significand`, `vfp_single_fsqrt`, `vfp_compare`, conversion helpers, `vfp_single_multiply`, `vfp_single_add`, `vfp_single_multiply_accumulate`, arithmetic operations `fmac/fnmac/fmsc/fnmsc/fmul/fnmul/fadd/fsub/fdiv`, and dispatcher `vfp_single_cpdo`. Tables `fops_ext[]` and `fops[]` map opcodes.

### Control Flow
`vfp_single_cpdo()` extracts single register operands, fetches values, dispatches by opcode, and writes results. Arithmetic paths unpack IEEE single values, handle special classes, perform significand math, normalize/round, and return exception flags. Conversion paths translate between single, double, signed integers, and unsigned integers with FPSCR-controlled rounding.

### State, Persistence, And Dependencies
Uses transient `struct vfp_single` values and accesses actual VFP registers through `vfp_get_float`/`vfp_put_float`. Persistent state is FPSCR flags and the current thread's VFP register image. Depends on `vfp.h` and `vfpinstr.h`.

### Integration Points
Called by `vfp_emulate_instruction()` for bounced single-precision CPDO instructions; shares exception propagation with `vfpmodule.c` and double conversion with `vfpdouble.c`.

### Risks
Single precision still has complex IEEE behavior around denormals, signed zero, NaNs, saturation, and exact inexact/underflow flag timing. Register extraction differs from double register encodings.

### Test Signals
Run single-precision FP conformance vectors, conversion boundary cases, denormal/NaN tests, and tests that force software emulation rather than hardware completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/vfp/vfpsingle.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/xen/Makefile -->
## sources/distributed-fs/ceph-client/arch/arm/xen/Makefile

### Purpose
Builds ARM Xen guest support objects.

### Important APIs, Types, And Functions
Adds `enlighten.o`, `hypercall.o`, `grant-table.o`, `p2m.o`, and `mm.o` to `obj-y`.

### Control Flow
Kbuild compiles all ARM Xen implementation files when the directory is selected by the architecture build.

### State, Persistence, And Dependencies
Build metadata only; runtime Xen state is in the listed objects.

### Integration Points
Links Xen discovery, hypercalls, grant-table support, p2m mapping, and DMA/cache handling into ARM kernels with Xen support.

### Risks
Object omissions produce missing symbols for generic Xen code or broken runtime initialization.

### Test Signals
Build ARM Xen configs and boot a Xen HVM/dom0 guest to ensure all exported hypercall and p2m symbols resolve.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/xen/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/xen/enlighten.c -->
## sources/distributed-fs/ceph-client/arch/arm/xen/enlighten.c

### Purpose
Initializes Xen support on ARM guests: detects Xen from DT/ACPI, maps shared info and grant frames, sets event-channel IRQs, registers vCPU info, timekeeping hooks, reboot/poweroff hooks, and exports hypercall symbols.

### Important APIs, Types, And Functions
Key functions include `xen_unmap_domain_gfn_range`, `xen_read_wallclock`, `xen_pvclock_gtod_notify`, `xen_starting_cpu`, `xen_dying_cpu`, `xen_reboot`, `xen_early_init`, `arch_xen_unpopulated_init`, `xen_dt_guest_init`, `xen_acpi_guest_init`, `xen_guest_init`, and `xen_late_init`. Globals include `xen_start_info`, `xen_domain_type`, `HYPERVISOR_shared_info`, `xen_vcpu`, `xen_vcpu_id`, `xen_events_irq`, and `xen_grant_frames`.

### Control Flow
Early boot scans `/hypervisor` DT nodes, records Xen version and features, and sets domain type/flags. Guest init locates callback IRQs, maps the shared info page via `XENMEM_add_to_physmap`, allocates per-CPU vCPU info, sets up grant frames, initializes event channels, requests the per-CPU event IRQ, and registers CPU hotplug startup. Late init installs reboot/poweroff hooks, syncs wallclock for non-initial domains, and starts Xen time/runstate support.

### State, Persistence, And Dependencies
Persistent state is global Xen domain metadata, shared info mapping, per-CPU vCPU pointers, grant frame location, and event IRQ. Dependencies include Xen hypercall interfaces, event channels, grant tables, OF/ACPI parsing, EFI proxy setup, pvclock, cpuidle/cpufreq disablement, and virtio restricted memory access.

### Integration Points
This is the ARM Xen architecture entry point for generic Xen subsystems, timekeeping, interrupts, grant tables, suspend stubs, and module-visible hypercall wrappers.

### Risks
Bad DT/ACPI parsing can leave Xen detected but without an event IRQ or grant-table region. Per-CPU vCPU registration cannot be repeated incorrectly. Shared-info mapping failures are fatal. Clock synchronization hypercalls are deliberately rate-limited.

### Test Signals
Boot dom0 and domU ARM guests via DT and ACPI, exercise CPU hotplug, event channels, grant table I/O, Xen wallclock updates, reboot/poweroff, and EFI-runtime proxy paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/xen/enlighten.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/xen/grant-table.c -->
## sources/distributed-fs/ceph-client/arch/arm/xen/grant-table.c

### Purpose
Provides ARM-specific grant-table architecture hooks, mostly stubs because ARM uses auto-translated grant frames set up elsewhere.

### Important APIs, Types, And Functions
Defines `arch_gnttab_map_shared`, `arch_gnttab_unmap`, `arch_gnttab_map_status`, and `arch_gnttab_init`.

### Control Flow
Shared/status mapping hooks return `-ENOSYS`, unmap is a no-op, and init returns success. Generic Xen grant code falls back to the ARM auto-xlat setup path.

### State, Persistence, And Dependencies
No local persistent state. Depends on Xen grant-table interfaces and page types.

### Integration Points
Satisfies generic grant-table architecture hooks while actual frame setup is handled from `enlighten.c` through `gnttab_setup_auto_xlat_frames` or ballooned pages.

### Risks
If generic Xen grant-table expectations change, these stubs may become insufficient. Returning success from init assumes all required setup happened before generic grant use.

### Test Signals
Run Xen blk/net front/back drivers using grants and verify generic code does not call unsupported shared/status mapping paths on ARM.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/xen/grant-table.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/xen/hypercall.S -->
## sources/distributed-fs/ceph-client/arch/arm/xen/hypercall.S

### Purpose
Implements ARM Xen hypercall wrappers using the Xen-specific HVC immediate and ARM register calling convention.

### Important APIs, Types, And Functions
Exports wrappers such as `HYPERVISOR_xen_version`, `console_io`, `grant_table_op`, `sched_op`, `event_channel_op`, `hvm_op`, `memory_op`, `physdev_op`, `vcpu_op`, `platform_op_raw`, `multicall`, `vm_assist`, `dm_op`, and `privcmd_call`.

### Control Flow
Wrapper macros move the hypercall number into `r12`, issue `HVC #0xEA1`, and return with result in `r0`. Five-argument calls save/load `r4` for the fifth argument. `privcmd_call` remaps user-provided arguments into hypercall registers, temporarily enables kernel user access around the HVC, then disables it.

### State, Persistence, And Dependencies
No persistent storage. Depends on Xen hypercall numbers, `__HVC`, ARM ABI, and uaccess enable/disable assembler macros.

### Integration Points
Called by ARM Xen C code and exported for generic Xen subsystems and privcmd userspace forwarding.

### Risks
Register save/restore bugs corrupt callers. `privcmd_call` must bracket user memory access exactly or create security exposure. Hypercall immediate must remain Xen's ARM tag.

### Test Signals
Boot Xen guests, run grant/event/memory hypercall paths, exercise `/dev/xen/privcmd`, and inspect disassembly for register convention correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/xen/hypercall.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/xen/mm.c -->
## sources/distributed-fs/ceph-client/arch/arm/xen/mm.c

### Purpose
Handles ARM Xen DMA/cache coherency decisions, Xen SWIOTLB initialization, and grant-table cache flush hypercall support.

### Important APIs, Types, And Functions
Key functions are `xen_swiotlb_gfp`, `dma_cache_maint`, `xen_dma_sync_for_cpu`, `xen_dma_sync_for_device`, `xen_arch_need_swiotlb`, and `xen_mm_init`. State includes `hypercall_cflush`.

### Control Flow
Init detects Xen SWIOTLB need, allocates late SWIOTLB memory with DMA-capable GFP flags, probes `GNTTABOP_cache_flush`, and records availability. DMA sync functions translate DMA handles to physical addresses and issue cache flush hypercalls page by page. `xen_arch_need_swiotlb()` requests bounce buffering when cache-flush hypercalls are unavailable, memory is foreign, and the device is noncoherent.

### State, Persistence, And Dependencies
Persistent state is SWIOTLB allocation and the `hypercall_cflush` capability flag. Dependencies include DMA mapping APIs, memblock ranges, Xen grant-table hypercalls, `xen_swiotlb_detect`, and device coherency attributes.

### Integration Points
Used by generic Xen SWIOTLB and DMA paths so ARM guests can safely DMA to local or foreign memory.

### Risks
Cache maintenance on foreign/highmem pages is correctness-critical for noncoherent devices. Incorrect bounce-buffer decisions can cause data corruption. Page-boundary handling must match Xen page size.

### Test Signals
Run Xen guest network/block DMA under coherent and noncoherent device models, test foreign grant mappings, and verify cache flush hypercall fallback behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/xen/mm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/xen/p2m.c -->
## sources/distributed-fs/ceph-client/arch/arm/xen/p2m.c

### Purpose
Maintains ARM Xen physical-to-machine mappings for foreign grant pages using an RB tree.

### Important APIs, Types, And Functions
Defines `struct xen_p2m_entry`, global `phys_to_mach`, lock `p2m_lock`, and functions `__pfn_to_mfn`, `set_foreign_p2m_mapping`, `clear_foreign_p2m_mapping`, `__set_phys_to_machine_multi`, `__set_phys_to_machine`, and `p2m_init`.

### Control Flow
Mapping updates allocate an entry, take the write lock, insert into the RB tree by PFN, or remove an existing range when setting `INVALID_P2M_ENTRY`. Lookups take the read lock and find an entry whose PFN range covers the query. Grant map completion records MFNs; if recording fails it immediately unmaps that grant reference.

### State, Persistence, And Dependencies
Persistent state is the in-memory RB tree of PFN-to-MFN ranges protected by `p2m_lock`. Dependencies include Xen grant operations, RB tree APIs, spin/rw locks, and invalid mapping constants.

### Integration Points
Used by Xen DMA, grant-table, and page translation helpers to distinguish local and foreign machine frames.

### Risks
Overlapping or duplicate PFN entries are rejected but range-overlap beyond identical starts is not broadly merged. GFP_NOWAIT allocation can fail in mapping paths. Bad cleanup leaves stale foreign mappings and DMA/cache decisions wrong.

### Test Signals
Map/unmap grant pages repeatedly, run concurrent p2m lookups, inject allocation failures, and verify `__pfn_to_mfn` returns invalid after unmap.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/xen/p2m.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/Kbuild -->
## sources/distributed-fs/ceph-client/arch/arm64/Kbuild

### Purpose
Top-level ARM64 Kbuild file selecting architecture subdirectories and disabling branch profiling where unsafe.

### Important APIs, Types, And Functions
Adds `kernel/`, `mm/`, and `net/` unconditionally; conditionally adds `kvm/`, `xen/`, `hyperv/`, and `crypto/`. Adds `-DDISABLE_BRANCH_PROFILING` under `CONFIG_TRACE_BRANCH_PROFILING`.

### Control Flow
Kbuild evaluates config symbols and descends into selected subdirectories. Cleaning also covers `boot`.

### State, Persistence, And Dependencies
Build metadata only. Depends on configuration symbols for virtualization and crypto subsystems.

### Integration Points
Defines the ARM64 architecture build shape used by the global kernel build.

### Risks
Subdirectory selection errors omit entire architecture subsystems. Branch profiling must remain disabled for noinstr-sensitive code.

### Test Signals
Build ARM64 configs with KVM, Xen, Hyper-V, crypto, and trace branch profiling enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/Kconfig -->
## sources/distributed-fs/ceph-client/arch/arm64/Kconfig

### Purpose
Defines the ARM64 architecture configuration surface: base architecture capabilities, erratum workarounds, page/VA/PA geometry, CPU and memory features, security extensions, virtualization, boot, power management, and included subsystem Kconfigs.

### Important APIs, Types, And Functions
Major symbols include `ARM64`, `RUSTC_SUPPORTS_ARM64`, `PGTABLE_LEVELS`, `ARCH_SUPPORTS_UPROBES`, many `ARM64_ERRATUM_*` workarounds, page-size choices, `ARM64_VA_BITS`, `ARM64_PA_BITS`, `CPU_BIG_ENDIAN/LITTLE_ENDIAN`, `NR_CPUS`, `NUMA`, `PARAVIRT`, `XEN`, `ARM64_PTR_AUTH`, `ARM64_BTI`, `ARM64_MTE`, `ARM64_SVE`, `ARM64_SME`, `RANDOMIZE_BASE`, `EFI`, and many included subsystem sources.

### Control Flow
Kconfig selects generic kernel capabilities from `config ARM64`, then presents menus for errata, kernel features, boot, power management, CPU power, ACPI, KVM, livepatch, and architectural extensions. Choices and defaults derive page-table levels, virtual address bits, physical address bits, endianness, and security feature enablement.

### State, Persistence, And Dependencies
The persistent output is the kernel `.config` and generated config headers. Dependencies encode compiler, assembler, linker, CPU feature, firmware, and subsystem constraints. It also sources `arch/arm64/Kconfig.platforms`, `arch/arm64/kvm/Kconfig`, and many generic Kconfigs.

### Integration Points
Controls nearly every ARM64 build and runtime integration point: memory management, tracing, BPF, KASAN, CFI, SCS, PAC/BTI, MTE, SVE/SME, ACPI/EFI, Xen/KVM, NUMA, hibernation, and boot command line handling.

### Risks
Defaults can enable hardware workarounds or features that depend on firmware/toolchain support. Incorrect dependency expressions may expose unsupported instructions, ABI flags, or security features. Config combinations around page size, VA/PA bits, KASAN, LPA2, and compat affect ABI and boot viability.

### Test Signals
Run `allnoconfig`, `defconfig`, `allyesconfig`, big-endian, KASAN, KVM, Xen, EFI, SVE/SME, MTE, PAC/BTI, and multiple page-size builds; boot representative configurations and validate generated `autoconf.h`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/Makefile -->
## sources/distributed-fs/ceph-client/arch/arm64/Makefile

### Purpose
Defines ARM64 architecture compiler, assembler, linker, Rust, image, vDSO, install, and help rules for the kernel build.

### Important APIs, Types, And Functions
Sets `LDFLAGS_vmlinux`, `KBUILD_CFLAGS`, `KBUILD_AFLAGS`, `KBUILD_RUSTFLAGS`, endian flags, branch protection flags, stack protector sysreg flags, KASAN shadow defines, `KBUILD_IMAGE`, `BOOT_TARGETS`, `archprepare`, `vdso_prepare`, `virtconfig`, and `archhelp`.

### Control Flow
The Makefile detects toolchain features, appends flags according to config, selects assembler architecture, sets endian and linker targets, defines image targets that recurse into `arch/arm64/boot`, generates tools during `archprepare`, and builds vDSO artifacts after `prepare0`.

### State, Persistence, And Dependencies
Build state is generated flags and artifacts. Dependencies include compiler/linker feature tests, `asm-offsets.h`, vDSO build directories, EFI libstub, Kconfig symbols, and compression/install scripts.

### Integration Points
This file is included by the global top-level Makefile and controls how every ARM64 object and final boot image is produced.

### Risks
Toolchain flag selection is fragile: wrong PAC/BTI, SCS, FPU, unwind, KASAN, endian, or relocation flags can break boot or ABI. vDSO generation depends on prepare ordering.

### Test Signals
Build with GCC and Clang/LLVM, LLD and GNU ld, little/big endian, relocatable/KASLR, PAC/BTI/SCS, KASAN modes, Rust enabled, EFI zboot, and compat vDSO.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/Makefile -->
## sources/distributed-fs/ceph-client/arch/arm64/boot/Makefile

### Purpose
Builds ARM64 bootable kernel image formats from `vmlinux`, including raw `Image`, compressed variants, FIT image, and EFI zboot support.

### Important APIs, Types, And Functions
Defines `OBJCOPYFLAGS_Image`, `targets`, rules for `Image`, `Image.bz2`, `Image.gz`, `Image.lz4`, `Image.lzma`, `Image.lzo`, `Image.zst`, `Image.xz`, `image.fit`, and EFI zboot variables.

### Control Flow
`Image` is produced by objcopy from `vmlinux`; compression targets depend on `Image` and call standard Kbuild compression commands. `image.fit` depends on `Image` plus the DTB list. EFI zboot includes the EFI libstub zboot makefile and forwards BTI CFI settings.

### State, Persistence, And Dependencies
Persistent artifacts are boot images under `arch/arm64/boot`. Dependencies include `vmlinux`, compression tools, DTB lists, `NM`, objcopy, and EFI libstub machinery.

### Integration Points
Receives recursive calls from `arch/arm64/Makefile` and produces images consumed by bootloaders, installers, and EFI stub flows.

### Risks
Compression tool absence or stale DTB lists breaks specific targets. Objcopy flags intentionally strip notes/comments; changing them affects boot image contents. EFI zboot symbol injection depends on `_kernel_codesize`.

### Test Signals
Build all boot targets, inspect image sizes and `file` output, boot `Image.gz` and `vmlinuz.efi`, and validate FIT includes expected DTBs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/Makefile -->
## sources/distributed-fs/ceph-client/arch/arm64/boot/dts/Makefile

### Purpose
Lists ARM64 vendor DTS subdirectories to include in the device-tree build.

### Important APIs, Types, And Functions
Uses `subdir-y +=` for vendors including actions, airoha, allwinner, altera, amazon, amd, amlogic, apple, arm, broadcom, mediatek, qcom, renesas, rockchip, ti, xilinx, and others.

### Control Flow
Kbuild descends into every listed vendor directory during DTB builds.

### State, Persistence, And Dependencies
Build metadata only. Persistent outputs are generated by child Makefiles. Depends on each vendor directory existing and containing valid DTB rules.

### Integration Points
Feeds `make dtbs` and ARM64 boot image/FIT generation with all vendor-specific device trees.

### Risks
Missing a vendor subdir excludes all its boards from DTB builds. Adding a subdir without valid rules can break global `dtbs`.

### Test Signals
Run `make ARCH=arm64 dtbs` and confirm each listed vendor emits expected DTB targets or no-op behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/actions/Makefile -->
## sources/distributed-fs/ceph-client/arch/arm64/boot/dts/actions/Makefile

### Purpose
Declares Actions Semi ARM64 DTB targets.

### Important APIs, Types, And Functions
Adds `s700-cubieboard7.dtb` and `s900-bubblegum-96.dtb` under `CONFIG_ARCH_ACTIONS`.

### Control Flow
When `ARCH_ACTIONS` is enabled, Kbuild builds the listed DTBs from matching DTS files.

### State, Persistence, And Dependencies
State is build metadata; outputs are DTB files. Depends on the referenced DTS sources and the platform Kconfig symbol.

### Integration Points
Participates in ARM64 `dtbs` and FIT image generation for Actions boards.

### Risks
Renamed or removed DTS files leave stale DTB rules. Config gating must match the platform symbol.

### Test Signals
Build `make ARCH=arm64 dtbs CONFIG_ARCH_ACTIONS=y` and validate both DTBs compile with `dtc`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/actions/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/airoha/Makefile -->
## sources/distributed-fs/ceph-client/arch/arm64/boot/dts/airoha/Makefile

### Purpose
Declares the Airoha ARM64 DTB target.

### Important APIs, Types, And Functions
Adds `en7581-evb.dtb` under `CONFIG_ARCH_AIROHA`.

### Control Flow
Kbuild emits the DTB only when Airoha platform support is selected.

### State, Persistence, And Dependencies
Build metadata only; depends on `en7581-evb.dts` and `ARCH_AIROHA`.

### Integration Points
Adds Airoha evaluation board device tree coverage to ARM64 `dtbs`.

### Risks
Single-target directory means stale naming immediately removes Airoha board output.

### Test Signals
Build Airoha DTBs and run device-tree compiler warning checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/airoha/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/allwinner/Makefile -->
## sources/distributed-fs/ceph-client/arch/arm64/boot/dts/allwinner/Makefile

### Purpose
Lists Allwinner/Sunxi ARM64 DTB targets for A64, H5, H6, H313/H616/H618/H700, A100/A133, and newer sun55i boards.

### Important APIs, Types, And Functions
All entries are `dtb-$(CONFIG_ARCH_SUNXI) += ...` for boards such as Pine64, PinePhone, Banana Pi, Orange Pi, Libretech, Tanix, Anbernic, Cubie, Avaota, and X96 variants.

### Control Flow
When `ARCH_SUNXI` is enabled, Kbuild builds the entire listed board set from matching DTS files.

### State, Persistence, And Dependencies
State is the DTB target list. Depends on board DTS sources and shared Allwinner include files.

### Integration Points
Feeds `make dtbs` and boot packaging for a broad set of Allwinner ARM64 boards.

### Risks
Large board lists are prone to stale target names and missed additions. One config gate means all listed boards build together, so a single bad DTS can fail Sunxi DTB coverage.

### Test Signals
Run `make ARCH=arm64 dtbs` with `ARCH_SUNXI`, watch `dtc` warnings, and boot-test representative boards from each SoC family.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/allwinner/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/altera/Makefile -->
## sources/distributed-fs/ceph-client/arch/arm64/boot/dts/altera/Makefile

### Purpose
Declares Intel/Altera SoCFPGA Stratix10 ARM64 DTB targets.

### Important APIs, Types, And Functions
Adds `socfpga_stratix10_socdk.dtb`, `socfpga_stratix10_socdk_emmc.dtb`, `socfpga_stratix10_socdk_nand.dtb`, and `socfpga_stratix10_swvp.dtb` under `CONFIG_ARCH_INTEL_SOCFPGA`.

### Control Flow
Kbuild builds these DTBs when Intel SoCFPGA support is configured.

### State, Persistence, And Dependencies
Build metadata only; depends on Stratix10 DTS files and common SoCFPGA includes.

### Integration Points
Adds Stratix10 board device trees to ARM64 DTB builds.

### Risks
Multiline target continuation must remain syntactically correct; stale board DTS names break all listed variants.

### Test Signals
Build Intel SoCFPGA DTBs and validate eMMC/NAND variant DTs with `dtc`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/altera/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/amazon/Makefile -->
## sources/distributed-fs/ceph-client/arch/arm64/boot/dts/amazon/Makefile

### Purpose
Declares Amazon Annapurna Labs Alpine ARM64 DTB targets.

### Important APIs, Types, And Functions
Adds `alpine-v2-evp.dtb` and `alpine-v3-evp.dtb` under `CONFIG_ARCH_ALPINE`.

### Control Flow
Kbuild builds the two evaluation platform DTBs when Alpine platform support is enabled.

### State, Persistence, And Dependencies
Build metadata only; depends on matching DTS files and Alpine platform Kconfig.

### Integration Points
Includes Amazon Alpine boards in ARM64 DTB builds and boot packaging.

### Risks
Board coverage is limited to listed EVP variants; new DTS files require explicit target additions.

### Test Signals
Build with `ARCH_ALPINE`, run `dtc` validation, and boot-test Alpine v2/v3 DTBs where hardware or emulation is available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/amazon/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/amd/Makefile -->
## sources/distributed-fs/ceph-client/arch/arm64/boot/dts/amd/Makefile

### Purpose
Declares AMD-related ARM64 DTB targets for Pensando Elba and AMD Seattle platforms.

### Important APIs, Types, And Functions
Adds `elba-asic.dtb` under `CONFIG_ARCH_PENSANDO` and `amd-overdrive-rev-b0.dtb`/`amd-overdrive-rev-b1.dtb` under `CONFIG_ARCH_SEATTLE`.

### Control Flow
Kbuild builds DTBs according to the selected platform symbols.

### State, Persistence, And Dependencies
Build metadata only; depends on the DTS files for Elba ASIC and AMD Overdrive revisions.

### Integration Points
Feeds ARM64 `dtbs` with AMD/Pensando platform device trees.

### Risks
Separate config gates mean platform symbol drift can silently omit targets. Hardware revisions must map to correct DTB names.

### Test Signals
Build DTBs with `ARCH_PENSANDO` and `ARCH_SEATTLE`, validate `dtc` output, and boot-test on matching board revisions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/amd/Makefile -->
