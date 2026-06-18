# Group Research: group_1182_netbsd_src_sources_os_bsd_netbsd_src_lib_Makefile_sources_os_bsd_ne_e3558c4f452c

Scope verified against `Docs/research_subset_a.md`: all files are under `sources/os/bsd/netbsd-src`, which is included in subset A. Every listed source file was read completely and summarized separately below.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/Makefile

Read completely: 356 lines.

Top-level NetBSD library build orchestrator. It orders `csu`, optional GCC runtime pieces, `libc`, `i18n_module`, base libraries, external libraries, and higher-level consumers through multiple `.WAIT` dependency barriers.

The file is mostly conditional build policy: feature flags such as `MKGCC`, `MKRUMP`, `MKZFS`, `MKDTRACE`, `MKPAM`, `MKKERBEROS`, `MKLLVMRT`, and machine options decide which library subtrees enter the build. It also pulls external `Makefile.subdir` fragments for OpenSSL, Heimdal, NetPGP, libevent, OpenLDAP, ATF, and other imported components.

Reliability notes: this file encodes build ordering, so incorrect `.WAIT` placement can create stale-destdir or missing-library failures rather than local compile errors.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/Makefile.inc

Read completely: 3 lines.

Shared make include for libraries under `lib`, currently only setting default warning level `WARNS?= 5`.

No runtime behavior. Its effect is build-wide compiler diagnostics unless a subdirectory overrides `WARNS`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/bumpversion -->
# File Research: sources/os/bsd/netbsd-src/lib/bumpversion

Read completely: 127 lines.

Shell utility for creating or bumping `shlib_version` files in library directories. Options support create mode (`-c`), dry-run reporting (`-n`), and major-version bumping (`-m`); the default increments the minor version.

For each directory, it validates the existing version file unless creating a new one, sources `major` and `minor`, computes the next values, and writes a replacement file via a temporary path.

Reliability notes: it sources version files directly as shell, so inputs are assumed trusted source-tree metadata. It uses a fixed `/tmp/bump$$` path and minimal quoting, consistent with old tree tooling rather than hardened temporary-file practice.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/bumpversion -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/checkoldver -->
# File Research: sources/os/bsd/netbsd-src/lib/checkoldver

Read completely: 151 lines.

Shell utility for listing obsolete shared-library version files in supplied directories. Its intended usage is piping output to removal commands after reviewing newer installed versions.

It iterates library basenames, compares versioned names in three forms (`major.minor.teeny`, `major.minor`, and `major`), tracks the newest seen for each form, and prints older paths through `delete`.

Reliability notes: it changes into each target directory and relies on shell glob expansion. One tiny-version comparison branch references `$5` where the parsed version fields are `$1`, `$2`, `$3`, which appears suspicious in the read source.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/checkoldver -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/checkver -->
# File Research: sources/os/bsd/netbsd-src/lib/checkver

Read completely: 238 lines.

Shell utility that checks whether installed or set-list shared libraries have versions greater than the source tree `shlib_version` about to be installed. It supports checking an installed directory (`-d`), distribution set lists (`-s`), or a caller-supplied library list (`-f`), with optional quiet mode and custom version-file path.

It derives the library name from an argument, `LIB=` in the current `Makefile`, or the current directory name; sources `major`, `minor`, and optional `teeny`; then scans matching `lib*.so.*` entries and reports offending newer versions.

Reliability notes: temporary library lists are created under `/tmp/checkver.$$`. The `fixone` awk snippet splits into `VER` but prints `V[...]`, which appears inconsistent in the read source and is worth checking before relying on teeny-version behavior.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/checkver -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/checkvers -->
# File Research: sources/os/bsd/netbsd-src/lib/checkvers

Read completely: 210 lines.

Wrapper around `checkver` that finds every `shlib_version` under the current directory and runs the per-library check for each. It supports installed-directory, set-list, or file-list modes and can optionally take a library name.

It builds or passes a library list, locates `shlib_version` files with `find`, invokes `checkver` from the script directory, suppresses duplicate headers after the first failure, and warns if the same inferred library appears in multiple source locations.

Reliability notes: it uses `/tmp/checkvers.$$` with mode `700`. The quiet-mode test reads `[ quiet -eq 1 ]` instead of `[ $quiet -eq 1 ]`, which appears to disable that branch as written.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/checkvers -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/csu/Makefile

Read completely: 23 lines.

Top-level C startup object makefile. It disables libc and generic sanitizers for startup code, selects an architecture directory from `CSU_MACHINE_ARCH`, `MACHINE_ARCH`, or `MACHINE_CPU`, then includes the architecture and common make fragments.

The selected `ARCHDIR` supplies CPU-specific `crt0.S`, `crti.S`, `crtn.S`, and optional `crtbegin` handling. Unsupported architectures stop at make time with an explicit error.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/aarch64/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/aarch64/Makefile.inc

Read completely: 5 lines.

AArch64 CSU flags include the architecture directory and define `HAVE_INITFINI_ARRAY`, selecting constructor/destructor array handling instead of legacy `.init`/`.fini` call lists.

It contains a commented-out `ELF_NOTE_MARCH_DESC` definition for machine-architecture ELF notes.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/aarch64/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/aarch64/crt0.S -->
# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/aarch64/crt0.S

Read completely: 45 lines.

AArch64 process entry stub. It aliases `_start` to `__start`, adapts the loader/kernel register convention by moving `x2` into `x1`, then branches to the common C startup routine `___start`.

This file contains no libc initialization itself; it only bridges machine entry state into `crt0-common.c`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/aarch64/crt0.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/aarch64/crtbegin.h -->
# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/aarch64/crtbegin.h

Read completely: 35 lines.

AArch64 `crtbegin.c` companion header. It marks `__do_global_ctors_aux` as a used constructor and, for shared objects, marks `__do_global_dtors_aux` as a used destructor.

This matches the `HAVE_INITFINI_ARRAY` build mode and avoids architecture-specific `.init`/`.fini` call stubs.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/aarch64/crtbegin.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/aarch64/crtend.S -->
# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/aarch64/crtend.S

Read completely: 48 lines.

AArch64 end-marker object for startup sections. It emits hidden/global end labels for `.eh_frame` and `.jcr`, each aligned and padded to pointer size.

It does not emit legacy constructor/destructor list sentinels because AArch64 uses init/fini arrays in this tree.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/aarch64/crtend.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/aarch64/crti.S -->
# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/aarch64/crti.S

Read completely: 41 lines.

AArch64 `crti` object. It includes the architecture assembly header and common `sysident.S`, thereby adding NetBSD ELF note sections to startup objects.

No `_init` or `_fini` prologue is needed because this architecture uses init/fini arrays.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/aarch64/crti.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/aarch64/crtn.S -->
# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/aarch64/crtn.S

Read completely: 3 lines.

AArch64 `crtn` placeholder. It documents that no epilogue code is required because AAPCS64 uses `.init_array` and `.fini_array`.

No runtime instructions are emitted here.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/aarch64/crtn.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/alpha/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/alpha/Makefile.inc

Read completely: 3 lines.

Alpha CSU flags add the architecture directory and define `ELFSIZE=64`.

These flags feed common startup code and ELF note generation for Alpha objects.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/alpha/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/alpha/crt0.S -->
# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/alpha/crt0.S

Read completely: 53 lines.

Alpha process entry stub. It aliases `_start` to `__start`, loads the global pointer, maps Alpha entry registers so `a0` is cleanup and `a1` is `ps_strings`, then calls `___start`.

The comments document the kernel/rtld entry convention: stack pointer, cleanup, object entry, and `ps_strings` arrive in registers.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/alpha/crt0.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/alpha/crtbegin.h -->
# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/alpha/crtbegin.h

Read completely: 49 lines.

Alpha `crtbegin.c` companion header. It injects `.init` and `.fini` section calls to `__do_global_ctors_aux` and `__do_global_dtors_aux`, reloading the global pointer before each call.

This is the architecture-specific hook that connects common constructor/destructor code to Alpha legacy init/fini sections.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/alpha/crtbegin.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/alpha/crtend.S -->
# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/alpha/crtend.S

Read completely: 55 lines.

Alpha end-marker object. It emits aligned zero terminators/end markers for `.ctors`, `.dtors`, `.eh_frame`, and `.jcr`.

These symbols delimit legacy constructor/destructor and runtime metadata lists consumed by `crtbegin` logic.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/alpha/crtend.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/alpha/crtfm.c -->
# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/alpha/crtfm.c

Read completely: 68 lines.

Alpha support object for GCC `-ffast-math`. It defines a local `__alpha_sysarch` syscall wrapper and a constructor that requests Alpha floating-point control changes.

The constructor sets `IEEE_MAP_DMZ|IEEE_MAP_UMZ` through `ALPHA_SET_FP_C`, mapping denormalized and underflow behavior for fast-math programs. This is included only for Alpha CSU builds.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/alpha/crtfm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/alpha/crti.S -->
# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/alpha/crti.S

Read completely: 55 lines.

Alpha `crti` prologue object. It includes common `sysident.S`, then opens `.init` and `.fini` function sections with `_init` and `_fini` labels.

Each section reserves stack space and saves return address/global pointer state; `crtn.S` supplies the matching restore/return tail.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/alpha/crti.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/alpha/crtn.S -->
# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/alpha/crtn.S

Read completely: 45 lines.

Alpha `crtn` epilogue object. It closes `.init` and `.fini` by restoring `gp` and `ra`, releasing the stack frame, and returning.

It must match the stack layout established by Alpha `crti.S`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/alpha/crtn.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/arm/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/arm/Makefile.inc

Read completely: 7 lines.

ARM CSU flags set the architecture include path and `ELFSIZE=32`. If `CPUFLAGS` contains an AAPCS ABI flag, it also defines `ELF_NOTE_MARCH_DESC` from `CSU_MACHINE_ARCH`.

This metadata lets generated ELF notes distinguish ARM ABI variants.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/arm/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/arm/crt0.S -->
# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/arm/crt0.S

Read completely: 54 lines.

ARM process entry stub. It aliases `_start` to `__start`, remaps incoming registers so `___start` receives cleanup and `ps_strings`, then branches to the common startup routine.

The file is intentionally minimal and delegates all libc/process initialization to `crt0-common.c`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/arm/crt0.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/arm/crtbegin.h -->
# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/arm/crtbegin.h

Read completely: 38 lines.

ARM `crtbegin.c` companion header for legacy init/fini sections. It injects branch-and-link calls to `__do_global_ctors_aux` in `.init` and `__do_global_dtors_aux` in `.fini`.

This connects common constructor/destructor handling to ARM non-EABI startup sections.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/arm/crtbegin.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/arm/crtend.S -->
# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/arm/crtend.S

Read completely: 55 lines.

ARM end-marker object. It emits aligned terminators and hidden end labels for `.ctors`, `.dtors`, `.eh_frame`, and `.jcr`.

These markers delimit legacy constructor/destructor lists and exception/JCR metadata.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/arm/crtend.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/arm/crti.S -->
# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/arm/crti.S

Read completely: 58 lines.

ARM `crti` prologue object. It includes NetBSD ELF identity notes through `sysident.S`, then defines `_init` and `_fini` function prologues in `.init` and `.fini`.

The prologue saves frame/link state using ARM stack-frame conventions; `crtn.S` provides the matching return sequence.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/arm/crti.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/arm/crtn.S -->
# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/arm/crtn.S

Read completely: 44 lines.

ARM `crtn` epilogue object. It closes `.init` and `.fini` by restoring frame pointer, stack pointer, and program counter from the frame created by `crti.S`.

This is part of the legacy section-bracketing startup object pair.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/arm/crtn.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/earm/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/earm/Makefile.inc

Read completely: 5 lines.

EABI ARM CSU flags include the architecture directory, define `HAVE_INITFINI_ARRAY`, and define `ELF_NOTE_MARCH_DESC` from `CSU_MACHINE_ARCH`.

This selects init/fini-array startup behavior and emits ARM machine-architecture ELF notes.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/earm/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/earm/crt0.S -->
# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/earm/crt0.S

Read completely: 61 lines.

EABI ARM process entry stub. It remaps cleanup and `ps_strings` registers, contains Thumb-aware stack alignment handling, and branches to `___start`.

The extra Thumb path preserves correct stack alignment before entering common C startup.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/earm/crt0.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/earm/crtbegin.h -->
# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/earm/crtbegin.h

Read completely: 50 lines.

EABI ARM `crtbegin.c` companion header. It marks constructor and shared-object destructor helpers with compiler attributes and, for static non-DWARF-EH builds, defines `find_exidx`.

The `find_exidx` helper exposes `__exidx_start`/`__exidx_end` through a weak alias `__gnu_Uwind_find_exidx`, supporting ARM unwind table discovery.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/earm/crtbegin.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/earm/crtend.S -->
# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/earm/crtend.S

Read completely: 53 lines.

EABI ARM end-marker object. It emits EABI attributes for wchar size, floating-point usage, stack alignment, and enum size, then marks `.eh_frame` and `.jcr` ends.

It omits legacy `.ctors`/`.dtors` sentinels because EABI ARM uses init/fini arrays here.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/earm/crtend.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/earm/crti.S -->
# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/earm/crti.S

Read completely: 41 lines.

EABI ARM `crti` object. It includes the ARM assembly header and common `sysident.S` for NetBSD ELF identity notes.

No legacy `_init`/`_fini` prologue is emitted because this variant relies on init/fini arrays.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/earm/crti.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/earm/crtn.S -->
# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/earm/crtn.S

Read completely: 3 lines.

EABI ARM `crtn` placeholder. It contains only the RCS identifier and no instructions.

No section epilogue is required in the init/fini-array startup model.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/earm/crtn.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/hppa/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/hppa/Makefile.inc

Read completely: 3 lines.

HPPA CSU flags include the architecture directory.

The architecture-specific assembly files provide the rest of the required startup section behavior.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/hppa/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/hppa/crt0.S -->
# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/hppa/crt0.S

Read completely: 65 lines.

HPPA process entry stub. It sets up the global offset table pointer using a PC-relative sequence, aliases `__start` and `_start`, and branches to `___start`.

The comments document the incoming register convention for stack pointer, cleanup, object entry, and `ps_strings`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/hppa/crt0.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/hppa/crtbegin.h -->
# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/hppa/crtbegin.h

Read completely: 43 lines.

HPPA `crtbegin.c` companion header. It injects `.init` and `.fini` calls to common constructor and destructor helper routines using HPPA branch-and-link syntax and delay-slot `nop`s.

This links common `crtbegin.c` logic into HPPA legacy init/fini sections.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/hppa/crtbegin.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/hppa/crtend.S -->
# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/hppa/crtend.S

Read completely: 56 lines.

HPPA end-marker object. It emits aligned zero terminators for `.ctors`, `.dtors`, `.eh_frame`, and `.jcr`, including hidden constructor/destructor end labels.

These markers are consumed by legacy constructor/destructor traversal.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/hppa/crtend.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/hppa/crti.S -->
# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/hppa/crti.S

Read completely: 55 lines.

HPPA `crti` prologue object. It includes `sysident.S` and defines a macro that emits HPPA section prologues with call info, stack-frame allocation, and return-pointer saving.

The macro is used to bracket `.init` and `.fini`; `crtn.S` supplies the matching epilogue macro.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/hppa/crti.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/hppa/crtn.S -->
# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/hppa/crtn.S

Read completely: 46 lines.

HPPA `crtn` epilogue object. It defines a macro that restores the return pointer and stack pointer for the `.init` and `.fini` sections.

This file must stay synchronized with the frame layout in HPPA `crti.S`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/hppa/crtn.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/i386/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/i386/Makefile.inc

Read completely: 5 lines.

i386 CSU flags define `ELFSIZE=32`.

The i386 directory supplies assembly `crtbegin.S`, so common `crtbegin.c` is not used for that object.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/i386/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/i386/crt0.S -->
# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/i386/crt0.S

Read completely: 48 lines.

i386 process entry stub. It aliases `_start` to `__start`, hides `___start`, and calls the common C startup routine using the i386 entry stack/register convention.

All high-level process initialization is delegated to `crt0-common.c`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/i386/crt0.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/i386/crtbegin.S -->
# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/i386/crtbegin.S

Read completely: 174 lines.

Hand-written i386 `crtbegin` object. It creates `.ctors`, `.dtors`, `.eh_frame`, `.jcr`, `__dso_handle`, and guard bytes, declares weak hooks for `__cxa_finalize`, frame registration, and Java class registration, then implements constructor/destructor helpers.

Constructors register EH frames and JCR classes, then walk constructors backward from `__CTOR_LIST_END__`; destructors optionally call `__cxa_finalize`, walk destructors forward, and deregister EH frames. The helpers are called from emitted `.init` and `.fini` section snippets.

Reliability notes: this assembly is ABI-sensitive and depends on GOT-relative addressing and exact list sentinel layout.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/i386/crtbegin.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/i386/crtend.S -->
# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/i386/crtend.S

Read completely: 52 lines.

i386 end-marker object. It emits `.ctors` `__CTOR_LIST_END__`, `.dtors`, `.eh_frame`, and `.jcr` zero terminators with 4-byte alignment.

These are paired with the custom i386 `crtbegin.S` traversal code.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/i386/crtend.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/i386/crti.S -->
# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/i386/crti.S

Read completely: 54 lines.

i386 `crti` prologue object. It includes NetBSD ELF identity notes and opens `.init`/`.fini` with aligned `_init` and `_fini` labels.

The prologue saves the current stack pointer into `%ebp`; `crtn.S` supplies the return instruction tail.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/i386/crti.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/i386/crtn.S -->
# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/i386/crtn.S

Read completely: 46 lines.

i386 `crtn` epilogue object. It closes `.init` and `.fini` with `ret` instructions.

It pairs with the section labels/prologue established by i386 `crti.S`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/i386/crtn.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/ia64/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/ia64/Makefile.inc

Read completely: 3 lines.

IA-64 CSU flags include the architecture directory.

The architecture-specific assembly handles IA-64 register stack and branch-register startup details.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/ia64/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/ia64/crt0.S -->
# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/ia64/crt0.S

Read completely: 58 lines.

IA-64 process entry stub. It aliases `_start` to `__start`, sets the memory stack pointer from incoming state, maps object/cleanup arguments, adjusts the register backing store with `alloc`, and calls `___start`.

This is the machine-specific bridge into common startup for IA-64’s register-stack ABI.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/ia64/crt0.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/ia64/crtbegin.h -->
# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/ia64/crtbegin.h

Read completely: 41 lines.

IA-64 `crtbegin.c` companion header. It injects calls to `__do_global_ctors_aux` and `__do_global_dtors_aux` into `.init` and `.fini` using `br.call.sptk.many`.

This connects common constructor/destructor logic to IA-64 legacy init/fini sections.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/ia64/crtbegin.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/ia64/crtend.S -->
# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/ia64/crtend.S

Read completely: 55 lines.

IA-64 end-marker object. It emits 8-byte aligned zero terminators for `.ctors`, `.dtors`, `.eh_frame`, and `.jcr`.

These delimit runtime metadata and legacy constructor/destructor lists.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/ia64/crtend.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/ia64/crti.S -->
# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/ia64/crti.S

Read completely: 62 lines.

IA-64 `crti` prologue object. It includes `sysident.S`, defines aligned `_init` and `_fini` procedures, and saves branch/register-stack state into local registers.

The matching restoration and return sequence is in IA-64 `crtn.S`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/ia64/crti.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/ia64/crtn.S -->
# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/ia64/crtn.S

Read completely: 46 lines.

IA-64 `crtn` epilogue object. It restores `b0` and `ar.pfs` for `.init` and `.fini`, then returns through `br.ret.sptk.many`.

It completes the IA-64 section procedures started in `crti.S`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/ia64/crtn.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/m68k/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/m68k/Makefile.inc

Read completely: 5 lines.

m68k CSU flags include the architecture directory and define `ELFSIZE=32`.

The architecture uses common C `crtbegin.c` plus m68k inline assembly hooks.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/m68k/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/m68k/crt0.S -->
# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/m68k/crt0.S

Read completely: 47 lines.

m68k process entry stub. It aliases `_start`, pushes `ps_strings` and cleanup arguments, then calls `___start`.

The stub documents the conversion from m68k entry registers to the common C startup calling convention.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/m68k/crt0.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/m68k/crtbegin.h -->
# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/m68k/crtbegin.h

Read completely: 45 lines.

m68k `crtbegin.c` companion header. It injects calls to constructor/destructor helpers into `.init` and `.fini`, using `bsrl` for PIC builds and `jsr` otherwise.

This is the m68k-specific glue between common `crtbegin.c` and legacy init/fini sections.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/m68k/crtbegin.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/m68k/crtend.S -->
# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/m68k/crtend.S

Read completely: 55 lines.

m68k end-marker object. It emits aligned zero terminators and constructor/destructor end labels for `.ctors`, `.dtors`, `.eh_frame`, and `.jcr`.

These markers are used by common constructor/destructor traversal.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/m68k/crtend.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/m68k/crti.S -->
# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/m68k/crti.S

Read completely: 50 lines.

m68k `crti` prologue object. It includes `sysident.S`, then defines aligned `_init` and `_fini` labels in their respective executable sections.

The actual section tail is provided by `crtn.S`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/m68k/crti.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/m68k/crtn.S -->
# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/m68k/crtn.S

Read completely: 44 lines.

m68k `crtn` epilogue object. It closes `.init` and `.fini` with `rts`.

This pairs with the section labels established by `crti.S`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/m68k/crtn.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/mips/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/mips/Makefile.inc

Read completely: 3 lines.

MIPS CSU flags include the architecture directory and define `ELFSIZE=32`.

MIPS startup uses architecture-specific GP handling in both entry and constructor/destructor stubs.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/mips/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/mips/crt0.S -->
# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/mips/crt0.S

Read completely: 59 lines.

MIPS process entry stub. It aliases `_start`, sets up the global pointer, remaps cleanup and `ps_strings` into argument registers, and jumps through the call16 relocation path to `___start`.

The file is sensitive to MIPS ABI/GP conventions and includes an explicit relocation annotation for the `jalr`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/mips/crt0.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/mips/crtbegin.h -->
# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/mips/crtbegin.h

Read completely: 66 lines.

MIPS `crtbegin.c` companion header. It injects `.init` and `.fini` calls to common constructor/destructor helpers, with special o32 code to restore/use `$gp`, load function addresses through GOT entries, and annotate `R_MIPS_JALR`.

Non-o32 builds use direct `jal` calls. This header is central to correct constructor/destructor dispatch under MIPS PIC/ABI rules.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/mips/crtbegin.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/mips/crtend.S -->
# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/mips/crtend.S

Read completely: 55 lines.

MIPS end-marker object. It emits pointer-size-aligned terminators for `.ctors`, `.dtors`, `.eh_frame`, and `.jcr`.

Alignment and padding are driven by MIPS pointer-size macros.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/mips/crtend.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/mips/crti.S -->
# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/mips/crti.S

Read completely: 62 lines.

MIPS `crti` prologue object. It includes `sysident.S`, opens `.init` and `.fini`, and preserves/restores GP setup needed by o32 builds.

The matching returns and frame cleanup live in MIPS `crtn.S`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/mips/crti.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/mips/crtn.S -->
# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/mips/crtn.S

Read completely: 52 lines.

MIPS `crtn` epilogue object. It closes `.init` and `.fini` with ABI-dependent restoration and `jr ra`.

The file accounts for o32/o64 versus other MIPS ABI stack and GP conventions.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/mips/crtn.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/or1k/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/or1k/Makefile.inc

Read completely: 5 lines.

OpenRISC CSU flags include the architecture directory and define `HAVE_INITFINI_ARRAY`.

A commented-out `ELF_NOTE_MARCH_DESC` line mirrors other init/fini-array architectures but is not active.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/or1k/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/or1k/crt0.S -->
# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/or1k/crt0.S

Read completely: 44 lines.

OpenRISC process entry stub. It aliases `_start` to `__start` and jumps/calls to the common `___start` routine.

No additional startup logic appears here; argument convention is handled by the platform ABI.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/or1k/crt0.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/or1k/crtbegin.h -->
# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/or1k/crtbegin.h

Read completely: 35 lines.

OpenRISC `crtbegin.c` companion header. It marks constructor helper execution through compiler constructor attributes and shared-object destructor helper execution through destructor attributes.

This matches the init/fini-array startup model.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/or1k/crtbegin.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/or1k/crtend.S -->
# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/or1k/crtend.S

Read completely: 48 lines.

OpenRISC end-marker object. It emits aligned hidden/global end labels for `.eh_frame` and `.jcr`.

No legacy constructor/destructor list terminators are needed with init/fini arrays.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/or1k/crtend.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/or1k/crti.S -->
# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/or1k/crti.S

Read completely: 41 lines.

OpenRISC `crti` object. It includes architecture assembly definitions and common `sysident.S`.

It emits NetBSD ELF note metadata but no legacy `.init`/`.fini` prologue.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/or1k/crti.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/or1k/crtn.S -->
# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/or1k/crtn.S

Read completely: 3 lines.

OpenRISC `crtn` placeholder. It contains only the RCS identifier and no code.

The architecture relies on init/fini arrays instead of bracketing legacy sections.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/or1k/crtn.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/powerpc/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/powerpc/Makefile.inc

Read completely: 3 lines.

PowerPC CSU flags include the architecture directory.

The assembly sources handle 32-bit and 64-bit PowerPC differences with `_LP64` conditionals.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/powerpc/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/powerpc/crt0.S -->
# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/powerpc/crt0.S

Read completely: 56 lines.

PowerPC process entry stub. It aliases `_start`, hides `___start`, sets up `_SDA_BASE_` for non-64-bit builds, then calls `___start`.

This file bridges the PowerPC entry ABI into common startup while preserving small-data-area setup for 32-bit code.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/powerpc/crt0.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/powerpc/crtbegin.h -->
# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/powerpc/crtbegin.h

Read completely: 36 lines.

PowerPC `crtbegin.c` companion header. It injects branch-and-link calls to constructor and destructor helpers into `.init` and `.fini`.

This links common constructor/destructor traversal into PowerPC legacy init/fini sections.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/powerpc/crtbegin.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/powerpc/crtend.S -->
# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/powerpc/crtend.S

Read completely: 71 lines.

PowerPC end-marker object. It emits pointer-size-appropriate zero terminators for `.ctors`, `.dtors`, `.eh_frame`, and `.jcr`, using `.quad` for `_LP64` and `.long` otherwise.

These delimit the legacy constructor/destructor and runtime metadata lists.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/powerpc/crtend.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/powerpc/crti.S -->
# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/powerpc/crti.S

Read completely: 58 lines.

PowerPC `crti` prologue object. It includes NetBSD ELF identity notes and opens `.init` and `.fini` with stack-frame setup, differing between `_LP64` and 32-bit builds.

`crtn.S` restores the saved state and returns.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/powerpc/crti.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/powerpc/crtn.S -->
# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/powerpc/crtn.S

Read completely: 54 lines.

PowerPC `crtn` epilogue object. It restores stack/register state for `.init` and `.fini`, with separate 32-bit and `_LP64` paths, then returns with `blr`.

It must match the frame created by PowerPC `crti.S`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/powerpc/crtn.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/riscv/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/riscv/Makefile.inc

Read completely: 5 lines.

RISC-V CSU flags include the architecture directory and define `HAVE_INITFINI_ARRAY`.

A commented-out machine-architecture ELF note line is present but inactive.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/riscv/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/riscv/crt0.S -->
# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/riscv/crt0.S

Read completely: 62 lines.

RISC-V process entry stub. It initializes `gp` with relaxation disabled, jumps to `___start`, and defines `_start_setgp` as a helper placed in `.preinit_array`.

The preinit helper ensures `gp` is set before static preinit routines run, which is essential for RISC-V global-pointer addressing.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/riscv/crt0.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/riscv/crtbegin.h -->
# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/riscv/crtbegin.h

Read completely: 35 lines.

RISC-V `crtbegin.c` companion header. It marks the constructor helper as a used compiler constructor and the shared-object destructor helper as a used compiler destructor.

This matches the RISC-V init/fini-array startup path.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/riscv/crtbegin.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/riscv/crtend.S -->
# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/riscv/crtend.S

Read completely: 48 lines.

RISC-V end-marker object. It emits pointer-size-aligned hidden/global end labels for `.eh_frame` and `.jcr`.

Legacy constructor/destructor list sentinels are not emitted because init/fini arrays are used.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/riscv/crtend.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/riscv/crti.S -->
# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/riscv/crti.S

Read completely: 41 lines.

RISC-V `crti` object. It includes the machine assembly header and common `sysident.S`.

It contributes NetBSD ELF note metadata and no legacy `.init`/`.fini` prologue.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/riscv/crti.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/riscv/crtn.S -->
# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/riscv/crtn.S

Read completely: 3 lines.

RISC-V `crtn` placeholder. It contains only the RCS identifier and no runtime instructions.

The architecture uses init/fini arrays rather than legacy section bracketing.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/riscv/crtn.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/sh3/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/sh3/Makefile.inc

Read completely: 5 lines.

SH3 CSU flags define `ELFSIZE=32`.

This architecture uses hand-written assembly `crtbegin.S` rather than the common C implementation.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/sh3/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/sh3/crt0.S -->
# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/sh3/crt0.S

Read completely: 59 lines.

SH3 process entry stub. It aliases `_start`, loads the `___start` address, maps cleanup from `r7` and `ps_strings` from `r9` into argument registers, and calls common startup.

It uses local call datum machinery suitable for SH3 relocation/PIC conventions.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/sh3/crt0.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/sh3/crtbegin.S -->
# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/sh3/crtbegin.S

Read completely: 366 lines.

Hand-written SH3 `crtbegin` object. It defines `.ctors`, `.dtors`, `.eh_frame`, `.jcr`, `__dso_handle`, guard bytes, weak frame/JCR/finalizer hooks, and full constructor/destructor helper routines.

The code has separate PIC/non-PIC datum macros, registers EH frames, optionally registers Java classes, walks constructors and destructors using list sentinels, calls `__cxa_finalize` for shared objects, and deregisters EH frames on shutdown. It emits `.init` and `.fini` calls to those helpers.

Reliability notes: this is dense ABI assembly; GOT setup, delay slots, and list traversal must match the SH3 toolchain’s emitted sections.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/sh3/crtbegin.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/sh3/crtend.S -->
# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/sh3/crtend.S

Read completely: 52 lines.

SH3 end-marker object. It emits aligned terminators for `.ctors`, `.dtors`, `.eh_frame`, and `.jcr`, including the `__CTOR_LIST_END__` label.

These markers are paired with SH3 `crtbegin.S`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/sh3/crtend.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/sh3/crti.S -->
# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/sh3/crti.S

Read completely: 62 lines.

SH3 `crti` prologue object. It includes `sysident.S` and opens `.init`/`.fini` by saving `r14`, procedure register, and current stack state.

The matching restore and return sequence is in SH3 `crtn.S`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/sh3/crti.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/sh3/crtn.S -->
# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/sh3/crtn.S

Read completely: 56 lines.

SH3 `crtn` epilogue object. It restores stack/frame and procedure register state for `.init` and `.fini`, then returns with `rts`.

It must match the prologue emitted by SH3 `crti.S`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/sh3/crtn.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/sparc/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/sparc/Makefile.inc

Read completely: 5 lines.

32-bit SPARC CSU flags define `ELFSIZE=32` and include the architecture directory.

The startup files use SPARC register-window and delay-slot conventions.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/sparc/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/sparc/crt0.S -->
# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/sparc/crt0.S

Read completely: 55 lines.

32-bit SPARC process entry stub. It clears the frame pointer, aligns/expands the stack to a standard frame, maps cleanup and `ps_strings` from global registers to output registers, and calls `___start`.

The file documents the startup argument convention used by kernel or rtld.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/sparc/crt0.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/sparc/crtbegin.h -->
# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/sparc/crtbegin.h

Read completely: 40 lines.

32-bit SPARC `crtbegin.c` companion header. It injects delay-slot-aware calls to constructor and destructor helpers into `.init` and `.fini`.

This links common constructor/destructor traversal into SPARC legacy startup sections.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/sparc/crtbegin.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/sparc/crtend.S -->
# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/sparc/crtend.S

Read completely: 55 lines.

32-bit SPARC end-marker object. It emits aligned `.ctors`, `.dtors`, `.eh_frame`, and `.jcr` zero terminators.

These delimit the lists used by common `crtbegin.c` helper traversal.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/sparc/crtend.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/sparc/crti.S -->
# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/sparc/crti.S

Read completely: 78 lines.

32-bit SPARC `crti` prologue object. It includes NetBSD ELF note metadata and opens aligned `_init` and `_fini` labels in executable sections.

The return tails are supplied by `crtn.S`, including SPARC delay-slot handling.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/sparc/crti.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/sparc/crtn.S -->
# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/sparc/crtn.S

Read completely: 74 lines.

32-bit SPARC `crtn` epilogue object. It closes `.init` and `.fini` with SPARC `ret` sequences and delay-slot instructions.

It pairs with the section labels from SPARC `crti.S`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/sparc/crtn.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/sparc64/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/sparc64/Makefile.inc

Read completely: 5 lines.

SPARC64 CSU flags define `ELFSIZE=64` and include the architecture directory.

SPARC64 startup uses 64-bit terminators and register declarations appropriate for v9 code.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/sparc64/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/sparc64/crt0.S -->
# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/sparc64/crt0.S

Read completely: 59 lines.

SPARC64 process entry stub. It aliases `_start`, declares scratch globals, maps cleanup and `ps_strings` to output registers, and branches predictably to `___start`.

The branch-delay slot passes the second argument, matching SPARC64 calling convention.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/sparc64/crt0.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/sparc64/crtbegin.h -->
# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/sparc64/crtbegin.h

Read completely: 40 lines.

SPARC64 `crtbegin.c` companion header. It injects `.init` and `.fini` calls to common constructor/destructor helpers with delay-slot `nop`s.

This is the SPARC64 legacy-section hook for common `crtbegin.c`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/sparc64/crtbegin.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/sparc64/crtend.S -->
# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/sparc64/crtend.S

Read completely: 55 lines.

SPARC64 end-marker object. It emits 8-byte aligned zero terminators for `.ctors`, `.dtors`, `.eh_frame`, and `.jcr`.

These markers are the 64-bit counterpart to the SPARC legacy list delimiters.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/sparc64/crtend.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/sparc64/crti.S -->
# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/sparc64/crti.S

Read completely: 78 lines.

SPARC64 `crti` prologue object. It includes common NetBSD ELF identity notes and opens aligned `_init` and `_fini` section labels.

`crtn.S` supplies matching returns for both sections.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/sparc64/crti.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/sparc64/crtn.S -->
# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/sparc64/crtn.S

Read completely: 74 lines.

SPARC64 `crtn` epilogue object. It closes `.init` and `.fini` with SPARC return sequences.

It is structurally parallel to the 32-bit SPARC `crtn.S`, with 64-bit assembly context.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/sparc64/crtn.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/vax/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/vax/Makefile.inc

Read completely: 3 lines.

VAX CSU flags include the architecture directory.

The VAX directory contains both common-header and hand-written assembly constructor support.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/vax/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/vax/crt0.S -->
# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/vax/crt0.S

Read completely: 42 lines.

VAX process entry stub. It aliases `_start` to `__start` and calls `___start` with two arguments using VAX `calls`.

The machine-specific work is limited to adapting the VAX entry ABI into the common startup routine.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/vax/crt0.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/vax/crtbegin.S -->
# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/vax/crtbegin.S

Read completely: 182 lines.

Hand-written VAX `crtbegin` object. It defines legacy constructor/destructor sentinels, EH/JCR sections, `__dso_handle`, guard storage, weak runtime hooks, and VAX assembly helpers for global constructor/destructor execution.

Constructors register EH frames and Java classes when available, then walk constructor entries backward; destructors call `__cxa_finalize` for shared builds, walk destructor entries, and deregister EH frames. It emits `.init` and `.fini` calls through VAX `calls`.

Reliability notes: list traversal and weak-hook calls are ABI-sensitive and must match VAX object layout and calling conventions.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/vax/crtbegin.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/vax/crtbegin.h -->
# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/vax/crtbegin.h

Read completely: 36 lines.

VAX `crtbegin.c` companion header. It injects VAX `calls` instructions to constructor and destructor helpers in `.init` and `.fini`.

In this tree VAX also has a full `crtbegin.S`; common make logic selects assembly when present.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/vax/crtbegin.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/vax/crtend.S -->
# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/vax/crtend.S

Read completely: 55 lines.

VAX end-marker object. It emits `.ctors`, `.dtors`, `.eh_frame`, and `.jcr` zero terminators with 4-byte alignment.

These delimit the lists consumed by VAX constructor/destructor startup code.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/vax/crtend.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/vax/crti.S -->
# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/vax/crti.S

Read completely: 52 lines.

VAX `crti` prologue object. It includes NetBSD ELF note metadata and opens `_init` and `_fini` labels, each with a VAX procedure entry mask word.

`crtn.S` supplies the returns.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/vax/crti.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/vax/crtn.S -->
# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/vax/crtn.S

Read completely: 44 lines.

VAX `crtn` epilogue object. It closes `.init` and `.fini` with `ret`.

This completes the VAX section procedures opened by `crti.S`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/vax/crtn.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/x86_64/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/x86_64/Makefile.inc

Read completely: 3 lines.

x86_64 CSU architecture include with only an RCS header.

The directory supplies hand-written `crtbegin.S` and 64-bit startup section assembly.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/x86_64/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/x86_64/crt0.S -->
# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/x86_64/crt0.S

Read completely: 48 lines.

x86_64 process entry stub. It aliases `_start`, adjusts the stack by 8 bytes, maps cleanup from `%rdx` to `%rdi` and `ps_strings` from `%rbx` to `%rsi`, then jumps to `___start`.

The stack adjustment aligns the call environment for the common C startup routine.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/x86_64/crt0.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/x86_64/crtbegin.S -->
# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/x86_64/crtbegin.S

Read completely: 156 lines.

Hand-written x86_64 `crtbegin` object. It defines `.ctors`, `.dtors`, `.eh_frame`, `.jcr`, 64-bit `__dso_handle`, guard bytes, and weak hooks for finalization, frame registration, and Java class registration.

Constructor code registers EH frames and JCR classes, then walks constructors backward. Destructor code optionally calls `__cxa_finalize`, walks destructors forward, and deregisters EH frames; `.init` and `.fini` snippets call these helpers.

Reliability notes: this assembly relies on RIP-relative addressing, 8-byte list entries, and sentinel layout matching `crtend.S`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/x86_64/crtbegin.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/x86_64/crtend.S -->
# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/x86_64/crtend.S

Read completely: 52 lines.

x86_64 end-marker object. It emits 8-byte aligned terminators for `.ctors`, `.dtors`, `.eh_frame`, and `.jcr`, including `__CTOR_LIST_END__`.

These markers delimit the lists traversed by x86_64 `crtbegin.S`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/x86_64/crtend.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/x86_64/crti.S -->
# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/x86_64/crti.S

Read completely: 52 lines.

x86_64 `crti` prologue object. It includes NetBSD ELF identity notes and opens aligned `_init` and `_fini` labels, subtracting 8 from `%rsp`.

`crtn.S` restores the stack and returns.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/x86_64/crti.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/x86_64/crtn.S -->
# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/x86_64/crtn.S

Read completely: 46 lines.

x86_64 `crtn` epilogue object. It adds 8 back to `%rsp` and returns in both `.init` and `.fini`.

This matches the stack adjustment performed by x86_64 `crti.S`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/arch/x86_64/crtn.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/common/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/csu/common/Makefile.inc

Read completely: 137 lines.

Common make fragment for building and installing NetBSD startup objects. It defines the object set (`crt0.o`, `gcrt0.o`, `crti.o`, `crtn.o`, `crtbegin.o`, `crtend.o`, `sysident.o`), adds PIC/PIE variants, selects common versus architecture-specific `crtbegin`, and strips `.ident` sections when configured.

It builds `crt0.o` and `gcrt0.o` by compiling both architecture `crt0.S` and common `crt0-common.c`, then partial-linking them. It generates `sysident_assym.h` through `genassym`, builds sparc64 code-model note objects, installs startup files into `${LIBDIR}`, and creates compatibility symlinks for PIC builds.

Reliability notes: this file is the central contract between architecture startup assembly and common C startup code; object naming and generated headers are tightly coupled.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/common/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/common/compident.S -->
# File Research: sources/os/bsd/netbsd-src/lib/csu/common/compident.S

Read completely: 66 lines.

Assembly template for compiler code-model ELF notes. It is used on architectures such as sparc64 where kernel virtual-address layout decisions depend on compiler memory model.

It emits `.note.netbsd.mcmodel` with NetBSD note name, note type, and caller-supplied `CONTENT`/`CONTENTLENGTH`, padded and aligned per ELF note rules.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/common/compident.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/common/crt0-common.c -->
# File Research: sources/os/bsd/netbsd-src/lib/csu/common/crt0-common.c

Read completely: 377 lines.

Common C startup routine for NetBSD programs. `___start` validates and stores `ps_strings`, initializes `environ`, `__ps_strings`, and `__progname`, runs preinit/init arrays or legacy `_init`, calls `_libc_init`, registers cleanup/fini handlers, optionally starts profiling for `gcrt0`, then exits with `main(argc, argv, environ)`.

It includes static-binary handling for init/fini arrays, IFUNC IPLT/IPLTA fixups for selected architectures, and x86 self-relocation for static PIE-style binaries using auxiliary vector program headers, dynamic relocation tags, RELR, REL/RELA, and relative relocations.

Reliability/security notes: this code runs before normal libc startup is complete, so it uses direct syscalls for fatal errors and aborts on unexpected relocation types. Changes here affect every dynamically or statically linked NetBSD process.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/common/crt0-common.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/common/crtbegin.c -->
# File Research: sources/os/bsd/netbsd-src/lib/csu/common/crtbegin.c

Read completely: 135 lines.

Common C implementation of `crtbegin` for architectures without custom assembly. It defines JCR, constructor/destructor list sentinels when legacy arrays are used, `__dso_handle`, weak references to finalizer/frame/JCR hooks, and helper routines for global constructors and destructors.

Constructors register EH frames, register Java classes when present, and walk the constructor list. Destructors guard against double execution, call `__cxa_finalize` for shared objects, walk destructor entries, and deregister EH frames.

Architecture-specific `crtbegin.h` files provide the actual `.init`/`.fini` calls or constructor/destructor attributes that make these helpers run.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/common/crtbegin.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/common/csu-common.h -->
# File Research: sources/os/bsd/netbsd-src/lib/csu/common/csu-common.h

Read completely: 40 lines.

Shared CSU header declaring historically common startup symbols also defined by libc: `__progname`, `environ`, and `__ps_strings`. It uses `__attribute__((__common__))` when available to preserve common-symbol behavior.

It also declares `_libc_init` as a used constructor. This header keeps startup objects and libc aligned on symbol definitions.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/common/csu-common.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/common/sysident.S -->
# File Research: sources/os/bsd/netbsd-src/lib/csu/common/sysident.S

Read completely: 89 lines.

Common assembly for NetBSD ELF identity notes. It emits `.note.netbsd.ident` with the NetBSD name and `__NetBSD_Version__`, plus `.note.netbsd.pax` with PaX metadata.

If `ELF_NOTE_MARCH_DESC` is defined, it also emits `.note.netbsd.march` describing the machine architecture/ABI. These notes let the kernel and tooling identify NetBSD binaries and ABI properties.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/csu/common/sysident.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/i18n_module/BIG5/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/i18n_module/BIG5/Makefile

Read completely: 5 lines.

Build file for the BIG5 i18n module. It explicitly builds `citrus_big5.c` together with shared property parser `citrus_prop.c`, then includes `bsd.lib.mk`.

This differs from most modules because BIG5 needs property parsing support.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/i18n_module/BIG5/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/i18n_module/DECHanyu/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/i18n_module/DECHanyu/Makefile

Read completely: 4 lines.

Build file for the DECHanyu Citrus module. It sets `SRCPRE=citrus_`, so the shared module make include derives the source as `citrus_dechanyu.c`.

The module is then built through `bsd.lib.mk`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/i18n_module/DECHanyu/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/i18n_module/EUC/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/i18n_module/EUC/Makefile

Read completely: 4 lines.

Build file for the EUC Citrus module. It uses `SRCPRE=citrus_`, causing the default source to resolve to `citrus_euc.c`.

It delegates the actual shared-library/module rules to `bsd.lib.mk`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/i18n_module/EUC/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/i18n_module/EUCTW/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/i18n_module/EUCTW/Makefile

Read completely: 4 lines.

Build file for the EUCTW Citrus module. It sets `SRCPRE=citrus_`, so the default source becomes `citrus_euctw.c`.

All install and library behavior comes from the shared i18n module make setup and `bsd.lib.mk`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/i18n_module/EUCTW/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/i18n_module/GBK2K/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/i18n_module/GBK2K/Makefile

Read completely: 5 lines.

Build file for the GBK2K Citrus module. It sets `SRCPRE=citrus_`, has a commented debug `CFLAGS+=-g`, and includes `bsd.lib.mk`.

The default source resolves to `citrus_gbk2k.c`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/i18n_module/GBK2K/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/i18n_module/HZ/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/i18n_module/HZ/Makefile

Read completely: 5 lines.

Build file for the HZ Citrus module. It explicitly builds `citrus_hz.c` plus `citrus_prop.c`, then includes `bsd.lib.mk`.

Like BIG5, HZ needs the Citrus property parser rather than only a single default module source.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/i18n_module/HZ/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/i18n_module/ISO2022/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/i18n_module/ISO2022/Makefile

Read completely: 4 lines.

Build file for the ISO2022 Citrus module. It sets `SRCPRE=citrus_`, causing the default source to resolve to `citrus_iso2022.c`.

It delegates to `bsd.lib.mk`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/i18n_module/ISO2022/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/i18n_module/JOHAB/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/i18n_module/JOHAB/Makefile

Read completely: 4 lines.

Build file for the JOHAB Citrus module. It uses the standard `SRCPRE=citrus_` convention, deriving `citrus_johab.c`.

Library/module rules come from `bsd.lib.mk`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/i18n_module/JOHAB/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/i18n_module/MSKanji/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/i18n_module/MSKanji/Makefile

Read completely: 4 lines.

Build file for the MSKanji Citrus module. It uses `SRCPRE=citrus_`, deriving the default source from the directory name.

The module is built by `bsd.lib.mk`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/i18n_module/MSKanji/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/i18n_module/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/i18n_module/Makefile

Read completely: 8 lines.

Subdirectory dispatcher for Citrus i18n modules. It lists encoding modules (`BIG5`, `DECHanyu`, `EUC`, `EUCTW`, `GBK2K`, `HZ`, `ISO2022`, `JOHAB`, `MSKanji`, `UES`, `UTF1632`, `UTF8`, `UTF7`, `VIQR`, `ZW`), iconv modules, and mapper modules.

It includes `bsd.subdir.mk` to build each module directory.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/i18n_module/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/i18n_module/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/i18n_module/Makefile.inc

Read completely: 28 lines.

Shared build include for Citrus i18n modules. It disables lint, profile builds, and PIC installation, sets the shared `shlib_version`, installs modules under `/usr/lib/i18n` or `/usr/lib/${MLIBDIR}/i18n`, and adds Citrus include paths and module metadata defines.

It derives `LIB` from the directory basename and defaults `SRCS` to `${SRCPRE:tl}${BASENAME:tl}.c`, with `.PATH` pointing at libc Citrus core and modules directories.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/i18n_module/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/i18n_module/UES/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/i18n_module/UES/Makefile

Read completely: 4 lines.

Build file for the UES Citrus module. It uses `SRCPRE=citrus_`, deriving the module source from the directory name.

The module is built through `bsd.lib.mk`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/i18n_module/UES/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/i18n_module/UTF1632/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/i18n_module/UTF1632/Makefile

Read completely: 4 lines.

Build file for the UTF1632 Citrus module. It follows the standard `SRCPRE=citrus_` convention.

The default source is derived from the directory basename and built through `bsd.lib.mk`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/i18n_module/UTF1632/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/i18n_module/UTF7/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/i18n_module/UTF7/Makefile

Read completely: 5 lines.

Build file for the UTF7 Citrus module. It sets `SRCPRE=citrus_` and includes `bsd.lib.mk`.

The file has a trailing blank line and no special flags.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/i18n_module/UTF7/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/i18n_module/UTF8/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/i18n_module/UTF8/Makefile

Read completely: 4 lines.

Build file for the UTF8 Citrus module. It uses `SRCPRE=citrus_`, deriving `citrus_utf8.c`.

The build is delegated to `bsd.lib.mk`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/i18n_module/UTF8/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/i18n_module/VIQR/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/i18n_module/VIQR/Makefile

Read completely: 4 lines.

Build file for the VIQR Citrus module. It uses the standard `SRCPRE=citrus_` source naming convention.

No module-specific flags are present.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/i18n_module/VIQR/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/i18n_module/ZW/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/i18n_module/ZW/Makefile

Read completely: 4 lines.

Build file for the ZW Citrus module. It sets `SRCPRE=citrus_` and includes `bsd.lib.mk`.

The module source is derived from the directory name.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/i18n_module/ZW/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/i18n_module/iconv_none/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/i18n_module/iconv_none/Makefile

Read completely: 4 lines.

Build file for the `iconv_none` Citrus module. It uses `SRCPRE=citrus_`, deriving `citrus_iconv_none.c`.

It follows the common i18n module build path through `bsd.lib.mk`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/i18n_module/iconv_none/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/i18n_module/iconv_std/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/i18n_module/iconv_std/Makefile

Read completely: 4 lines.

Build file for the `iconv_std` Citrus module. It sets `SRCPRE=citrus_`, deriving `citrus_iconv_std.c`.

No special flags are present beyond the common module include behavior.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/i18n_module/iconv_std/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/i18n_module/mapper_646/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/i18n_module/mapper_646/Makefile

Read completely: 4 lines.

Build file for the `mapper_646` Citrus mapper module. It uses `SRCPRE=citrus_`, deriving `citrus_mapper_646.c`.

It delegates to `bsd.lib.mk`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/i18n_module/mapper_646/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/i18n_module/mapper_none/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/i18n_module/mapper_none/Makefile

Read completely: 4 lines.

Build file for the `mapper_none` Citrus mapper module. It uses the standard `SRCPRE=citrus_` convention.

The module source is derived from the directory basename and built through `bsd.lib.mk`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/i18n_module/mapper_none/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/i18n_module/mapper_parallel/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/i18n_module/mapper_parallel/Makefile

Read completely: 4 lines.

Build file for the `mapper_parallel` module. Unlike most mapper directories, it explicitly sets `SRCS=citrus_mapper_serial.c`.

This means the parallel mapper is built from the serial mapper source name, likely relying on source-level conditionals or shared implementation naming.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/i18n_module/mapper_parallel/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/i18n_module/mapper_serial/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/i18n_module/mapper_serial/Makefile

Read completely: 4 lines.

Build file for the `mapper_serial` Citrus mapper module. It uses `SRCPRE=citrus_`, deriving `citrus_mapper_serial.c`.

It includes `bsd.lib.mk`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/i18n_module/mapper_serial/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/i18n_module/mapper_std/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/i18n_module/mapper_std/Makefile

Read completely: 4 lines.

Build file for the `mapper_std` Citrus mapper module. It uses `SRCPRE=citrus_`, deriving `citrus_mapper_std.c`.

No module-specific build flags are present.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/i18n_module/mapper_std/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/i18n_module/mapper_zone/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/i18n_module/mapper_zone/Makefile

Read completely: 4 lines.

Build file for the `mapper_zone` Citrus mapper module. It follows the standard `SRCPRE=citrus_` convention.

The default source resolves from the directory name and builds through `bsd.lib.mk`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/i18n_module/mapper_zone/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libarch/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/libarch/Makefile

Read completely: 35 lines.

Top-level build file for architecture-specific userland support libraries. It includes per-architecture `Makefile.inc` files for `alpha`, `arm`, `i386`, `m68k`, `powerpc`, `sparc`, and `x86_64`, adds generated assembly objects, and builds a library only if an included architecture fragment defines `SRCS`.

When building, the library name is `${MACHINE_CPU}` or `${MLIBDIR}` for compat builds except non-ARM compat handling, and it uses an architecture-specific `shlib_version` and export-symbol file. If no sources apply, only manpages are built.

Reliability notes: `.PATH` includes all architecture dirs, so source and export-symbol names must remain unambiguous.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libarch/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libarch/alpha/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libarch/alpha/Makefile.inc

Read completely: 5 lines.

Alpha `libarch` source selection. When `MACHINE_ARCH` is `alpha`, it adds `alpha_bus_window.c`, `alpha_pci_conf.c`, `alpha_pci_io.c`, and `alpha_pci_mem.c`.

Only the first three of those source files are in this research group.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libarch/alpha/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libarch/alpha/alpha_bus_window.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libarch/alpha/alpha_bus_window.c

Read completely: 114 lines.

Alpha userland helper for discovering and mapping bus windows, historically used to provide XFree86 bus-space access. `alpha_bus_getwindows` asks the kernel via `sysarch` for a count and each window’s translation metadata.

`alpha_bus_mapwindow` opens `/dev/mem`, computes the mapped size from bus range and address shift, and maps the physical/system window with read/write shared `mmap`. `alpha_bus_unmapwindow` unmaps the stored address and size.

Security/reliability notes: this code requires privileged `/dev/mem` access and maps hardware address space into userland; callers must treat returned windows as sensitive low-level hardware mappings.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libarch/alpha/alpha_bus_window.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libarch/alpha/alpha_pci_conf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libarch/alpha/alpha_pci_conf.c

Read completely: 73 lines.

Alpha userland helper for PCI configuration-space access. `alpha_pci_conf_read` populates `alpha_pci_conf_readwrite_args`, calls `sysarch(ALPHA_PCI_CONF_READWRITE)`, and returns `0xffffffffU` on failure.

`alpha_pci_conf_write` sets the write flag and value, then issues the same `sysarch` command without returning an error to the caller. This is a thin wrapper over kernel-mediated PCI config access.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libarch/alpha/alpha_pci_conf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libarch/alpha/alpha_pci_io.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libarch/alpha/alpha_pci_io.c

Read completely: 303 lines.

Alpha userland helper for x86-style programmed I/O to PCI/EISA/ISA I/O space. It maintains mapped PCI I/O windows, enables/disables mappings with `alpha_pci_io_enable`, and selects either swizzled or BWX byte/word-extension access operations based on bus-space flags.

The swizzled path computes sparse-space port addresses using address and size shifts, then packs/unpacks byte and word values inside 32-bit loads/stores with memory barriers. The BWX path uses EV56 byte/word load/store instructions through `<machine/bwx.h>` and direct dense-space offsets.

Reliability/security notes: failed window lookup prints a warning and aborts. Like `alpha_bus_window.c`, this exposes low-level hardware I/O through privileged mappings and assumes callers have intentionally enabled access.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libarch/alpha/alpha_pci_io.c -->