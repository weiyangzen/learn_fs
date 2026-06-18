# subset-b-000820 research

Grouped research for the requested s390 boot, crypto, and hypfs files. Each section is keyed by original source path for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/boot/ipl_report.c -->
# sources/distributed-fs/ceph-client/arch/s390/boot/ipl_report.c

Purpose: Handles early Secure IPL report discovery and preservation for the s390 boot decompressor. It reads the IPL report list behind the IPL parameter list, identifies certificate and component report blocks, reserves the original report while placement decisions are still being made, then copies certificate and component data into boot data for the decompressed kernel.

Important APIs/types/functions: Uses `struct ipl_pl_hdr`, `struct ipl_rl_hdr`, `struct ipl_rb_hdr`, `struct ipl_rb_certificates`, `struct ipl_rb_components`, and the `for_each_rb_entry` macro. Exports boot data such as `ipl_secure_flag`, `ipl_cert_list_addr`, `ipl_cert_list_size`, `early_ipl_comp_list_addr`, and `early_ipl_comp_list_size`. Key functions are `read_ipl_report()`, `save_ipl_cert_comp_list()`, `ipl_report_certs_intersects()`, `copy_components_bootdata()`, `copy_certificates_bootdata()`, and `get_cert_comp_list_size()`.

Control flow: `read_ipl_report()` first verifies that the copied IPL parameter block is valid and advertises an IPL report. It derives the report-list address from lowcore, walks bounded report blocks, records the certificate and component blocks, and reserves the whole report with `physmem_reserve(RR_IPLREPORT, ...)`. If either block is missing, it clears the certificate pointer and returns failure. Later `save_ipl_cert_comp_list()` sizes both lists, allocates a consolidated `RR_CERT_COMP_LIST` block, copies component entries and certificate payloads, frees `RR_IPLREPORT`, and clears `ipl_report_needs_saving`.

State and persistence: The file persists secure IPL state in bootdata-preserved globals consumed after decompression. The transient static pointers `certs` and `comps` reference the firmware-owned report while it is reserved. Once copied, `early_ipl_comp_list_*` and `ipl_cert_list_*` describe stable kernel-owned storage.

Dependencies and integration points: Integrates with `startup_kernel()` ordering, lowcore IPL parameter pointers, `physmem_info` reservation/allocation, `boot.h` intersection helpers, and UAPI IPL report structures. `physmem_info.c` calls `ipl_report_certs_intersects()` to avoid allocating over certificate bodies before they are copied.

Risks: Report walking trusts firmware lengths after simple bounds checks; malformed zero-length or overlapping blocks would be dangerous in early boot. Copying certificates from physical addresses must happen before the report reservation is released. Allocation alignment is only `sizeof(int)`, so consumers must not assume page alignment.

Test signals: Secure IPL boot with valid certificates/components, missing report-block fallbacks, KASLR-enabled placement avoiding certificate ranges, and checking exported certificate/component lists after boot are the strongest signals. Negative tests should corrupt report flags and block lengths in an s390 IPL test harness.

Source read size: 164 lines, complete file reviewed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/boot/ipl_report.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/boot/ipl_vmparm.c -->
# sources/distributed-fs/ceph-client/arch/s390/boot/ipl_vmparm.c

Purpose: Builds the boot-decompressor version of the s390 VM parameter parsing code by including `../kernel/ipl_vmparm.c` into the boot compilation unit.

Important APIs/types/functions: This file declares no local API. Its functional surface is inherited from the kernel implementation it includes, allowing the decompressor to share IPL VM parameter parsing behavior without maintaining a second copy.

Control flow: Compilation textual-includes the kernel source. Runtime control flow is therefore exactly the included implementation's flow, but linked into the boot environment with boot headers and symbol visibility.

State and persistence: No local state exists. Any state comes from the included IPL VM parameter implementation and from boot data symbols that the included file references.

Dependencies and integration points: Depends on the relative include path to `arch/s390/kernel/ipl_vmparm.c` and on that file staying compatible with the restricted boot environment. It is integrated by the boot Makefile as part of decompressor support.

Risks: Include-wrapper files are sensitive to implicit dependencies: if the kernel implementation begins depending on normal kernel services unavailable during decompression, boot builds can fail or early boot can fault. Review must cover the included file when behavior changes.

Test signals: s390 boot builds with changed IPL VM parameter parsing, IPL command-line/VM parameter parsing tests, and decompressor link checks are the relevant signals.

Source read size: 2 lines, complete file reviewed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/boot/ipl_vmparm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/boot/kaslr.c -->
# sources/distributed-fs/ceph-client/arch/s390/boot/kaslr.c

Purpose: Provides early entropy and placement selection helpers for s390 kernel address space layout randomization. It chooses a CPACF-backed random source and computes a valid randomized physical placement within usable memory while avoiding reserved ranges and dynamic boot allocations.

Important APIs/types/functions: Defines PRNG mode constants for TDES, SHA512, and TRNG, local `struct prno_parm` and `struct prng_parm`, `get_random()`, and `randomize_within_range()`. Internal helpers include `check_prng()`, `sort_reserved_ranges()`, and `iterate_valid_positions()`.

Control flow: `get_random()` probes CPACF support. It prefers true random (`cpacf_trng`), then SHA512 DRNG via PRNO seed/generate, then the older TDES PRNG via KMC after mixing TOD-clock entropy. `randomize_within_range()` snapshots `physmem_info.reserved`, sorts reservations, clamps the maximum to `get_physmem_alloc_pos()`, counts all aligned valid positions across usable physical ranges, draws one random position, and iterates again to return the selected address.

State and persistence: The file keeps no persistent global state. It reads current physical memory ranges, reservation arrays, and `physmem_alloc_pos`; all random parameters are stack-local and discarded after use.

Dependencies and integration points: Integrated by `startup.c` for physical vmlinux and amode31 placement and for virtual kernel placement entropy. It depends on CPACF query and instruction wrappers, TOD clock access, `physmem_info`, reservation types, and the boot logging path.

Risks: A zero or unsupported PRNG disables randomization by returning failure. Modulo reduction in `get_random()` can bias slot selection, though the placement domain is boot-only. Reservation handling must match `physmem_info.c` allocation semantics; missing a static reservation can cause overlap with initrd, IPL report certificates, decompressor storage, or relocated kernel image.

Test signals: Boots with `kaslr` enabled across machines with TRNG, SHA512 DRNG, and TDES-only CPACF support; forced allocation pressure; randomized vmlinux placement avoiding initrd/IPL report ranges; and fault-injection where CPACF support is absent or `get_random()` fails.

Source read size: 198 lines, complete file reviewed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/boot/kaslr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/boot/kmsan.c -->
# sources/distributed-fs/ceph-client/arch/s390/boot/kmsan.c

Purpose: Supplies a boot-time stub for `kmsan_unpoison_memory()` so code shared with instrumented kernel paths can link in the s390 boot environment.

Important APIs/types/functions: Defines `void kmsan_unpoison_memory(const void *address, size_t size)` as an empty function after including `linux/kmsan-checks.h`.

Control flow: Calls to `kmsan_unpoison_memory()` during decompressor execution are no-ops. There is no branching or side effect.

State and persistence: No state is read or written.

Dependencies and integration points: Exists because boot code may include or call APIs that are normally provided by KMSAN infrastructure, while the decompressor has no full sanitizer runtime. It complements `string.c`, which explicitly undefines KASAN/KMSAN before including shared string code.

Risks: This intentionally drops KMSAN semantics in early boot. If future boot code relies on unpoisoning for correctness rather than sanitizer bookkeeping, this stub would hide the mismatch.

Test signals: KMSAN-enabled s390 builds, decompressor link tests, and boot tests with memory instrumentation options enabled.

Source read size: 6 lines, complete file reviewed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/boot/kmsan.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/boot/machine_kexec_reloc.c -->
# sources/distributed-fs/ceph-client/arch/s390/boot/machine_kexec_reloc.c

Purpose: Reuses the s390 kernel kexec relocation implementation inside the boot build by textual inclusion.

Important APIs/types/functions: Declares no local functions or types. The exported behavior is provided by `../kernel/machine_kexec_reloc.c`.

Control flow: The compiler processes the shared kernel relocation source as part of the boot object, allowing early code to use the same relocation routines where required.

State and persistence: No local state exists. Any state belongs to the included kexec relocation implementation.

Dependencies and integration points: Depends on the shared kernel file remaining suitable for inclusion under boot build constraints and on relative path stability. It integrates with s390 kexec/crash boot support.

Risks: The wrapper can break if the shared file gains dependencies on normal kernel runtime services, instrumentation, or section annotations incompatible with the decompressor.

Test signals: s390 kexec and crash-kernel builds, decompressor link validation, and kexec relocation tests after modifying the included kernel file.

Source read size: 2 lines, complete file reviewed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/boot/machine_kexec_reloc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/boot/mem.S -->
# sources/distributed-fs/ceph-client/arch/s390/boot/mem.S

Purpose: Reuses the architecture library memory assembly routines in the boot environment.

Important APIs/types/functions: Declares no local symbols; all memory routine symbols come from `../lib/mem.S`.

Control flow: The assembler includes the shared s390 memory implementation directly, making low-level memory primitives available to decompressor code.

State and persistence: No local data is defined here.

Dependencies and integration points: Depends on `arch/s390/lib/mem.S` and on that file being safe to build for boot. These primitives underpin early `memcpy`, `memmove`, and related operations used by decompression and memory layout setup.

Risks: Assembly include wrappers are sensitive to section, relocation, and instrumentation assumptions. Changes in the shared memory assembly can affect boot long before normal exception handling is available.

Test signals: s390 decompressor build/link tests, early boot smoke tests, and objdump/relocation checks after changing shared memory assembly.

Source read size: 2 lines, complete file reviewed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/boot/mem.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/boot/pgm_check.c -->
# sources/distributed-fs/ceph-client/arch/s390/boot/pgm_check.c

Purpose: Implements early program-check reporting and fixup handling for the s390 boot decompressor. On unrecoverable faults it prints version, command line, KASLR offsets, PSW state, GPRs, stack trace, and last breaking-event address, then converts the faulting PSW to a disabled-wait PSW.

Important APIs/types/functions: Provides `print_stacktrace()` and `do_pgm_check()`. Internal helpers are `extable_insn()` and `ex_handler()`, using `__start___ex_table`, `__stop___ex_table`, `struct exception_table_entry`, `extable_fixup()`, `struct pt_regs`, `struct stack_frame`, and PSW bit accessors.

Control flow: `do_pgm_check()` first scans the early exception table; matching `EX_TYPE_FIXUP` entries redirect `regs->psw.addr` and return. Otherwise it optionally dumps the boot ring buffer, prints diagnostic context via `boot_emerg()`, walks the current boot stack from GPR15, and disables I/O and external interrupts before setting wait state.

State and persistence: It reads `kernel_version`, `early_command_line`, KASLR offsets, and boot debug flags. It mutates only the supplied `pt_regs` PSW to drive disabled wait after returning to low-level code.

Dependencies and integration points: Integrated with early exception vectors, exception-table annotations in boot code, `printk.c`, stack bounds `_stack_start/_stack_end`, lowcore state, protected-virtualization checks, and `kaslr.c` state.

Risks: Fault reporting itself must avoid additional faults. Symbol lookup and stack walking rely on decompressor symbol tables and valid stack-frame layout. Printing the command line is suppressed for protected-virtualization guests to avoid leaking protected inputs; future additions must preserve that property.

Test signals: Deliberate early exception-table fixups, injected boot program checks, KASLR-enabled and protected-guest crash logs, and stack trace correctness in decompressor symbols.

Source read size: 92 lines, complete file reviewed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/boot/pgm_check.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/boot/physmem_info.c -->
# sources/distributed-fs/ceph-client/arch/s390/boot/physmem_info.c

Purpose: Detects s390 physical memory limits and online ranges during decompressor execution, tracks reserved ranges, and provides top-down boot physical memory allocation with collision avoidance.

Important APIs/types/functions: Defines bootdata `struct physmem_info physmem_info`, `physmem_alloc_pos`, and `physmem_alloc_ranges`. Public functions include `add_physmem_online_range()`, `detect_max_physmem_end()`, `detect_physmem_online_ranges()`, `physmem_set_usable_limit()`, `physmem_reserve()`, `physmem_free()`, `physmem_alloc_range()`, `physmem_alloc()`, `physmem_alloc_or_die()`, `get_physmem_alloc_pos()`, and `dump_physmem_reserved()`.

Control flow: Memory limit detection tries DIAG 0x500 storage limit, SCLP read info, then binary search with `tprot()`. Online range detection tries SCLP storage info, SCLP memory size fallback, DIAG 0x260 extents, then a single 0..max range. Allocation walks online ranges from high to low, clamps to `physmem_alloc_pos`, rounds for alignment, skips reserved ranges and IPL certificate intersections, optionally chains repeated allocations of the same reservation type, and panics through `die_oom()` when required.

State and persistence: `physmem_info.online[]`, optional `online_extended`, `range_count`, `info_source`, `usable`, and `reserved[]` become bootdata for later kernel setup. Reserved ranges may form chains for repetitive top-down allocations. `physmem_alloc_pos` is the moving high-water mark for dynamic boot allocations.

Dependencies and integration points: Integrated with `startup.c`, `kaslr.c`, `ipl_report.c`, SCLP early memory queries, DIAG 0x260/0x500, `tprot`, sparsemem section sizing, and boot diagnostics.

Risks: This file is on the critical path for every later placement decision. Off-by-one conversion of inclusive firmware limits, range merging, chain allocation, and collision detection can corrupt kernel image, initrd, IPL report data, vmem tables, or KASAN shadow pages. Extended online range storage is itself allocated using early allocation state.

Test signals: Booting with SCLP, DIAG 500, DIAG 260, and binary-search fallback paths; memory holes; many storage increments requiring `online_extended`; low-memory allocation pressure; KASLR overlap tests; initrd rescue; and OOM diagnostics.

Source read size: 386 lines, complete file reviewed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/boot/physmem_info.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/boot/printk.c -->
# sources/distributed-fs/ceph-client/arch/s390/boot/printk.c

Purpose: Implements a compact printk-compatible logging path for the s390 boot decompressor, including a ring buffer, early SCLP console output, timestamps, limited formatting, and decompressor symbol resolution for `%pS`.

Important APIs/types/functions: Exports `boot_printk()`, `boot_rb_dump()`, `boot_console_loglevel`, `boot_ignore_loglevel`, `boot_earlyprintk`, `bootdebug`, `bootdebug_filter`, `boot_rb`, and `boot_rb_off`. Internal helpers include `boot_rb_add()`, `print_rb_entry()`, `as_hex()`, `as_dec()`, `strpad()`, `findsym()`, `strsym()`, `printk_loglevel()`, `boot_console_earlyprintk()`, and `add_timestamp()`.

Control flow: `boot_printk()` prefixes every message with a kernel loglevel marker, optionally appends a timestamp, parses a deliberately small format language (`%s`, `%pS`, `%d/%i`, `%u`, `%x`, width and length modifiers), writes the result into the boot ring buffer, and sends it to SCLP if loglevel and bootdebug filters allow. `boot_rb_dump()` prints buffered messages only if debug messages were not already emitted.

State and persistence: The ring buffer is a two-page bootdata buffer of NUL-separated strings with wraparound. Debug and loglevel settings are bootdata state parsed from the command line. Symbol lookup reads `_decompressor_syms_start/_end` generated by the linker script.

Dependencies and integration points: Used by nearly all boot files through `boot_debug`, `boot_warn`, `boot_emerg`, and `boot_panic` wrappers. It integrates with SCLP early printing, TOD clock conversion, protected guest checks in callers, and linker-provided decompressor symbols.

Risks: Unsupported format specifiers stop formatting at `out`, so new call sites must stay within the supported subset. Ring-buffer wrap leaves older messages behind without complex accounting. Symbol search assumes sorted NUL-separated decompressor symbols. Logging paths must remain fault-tolerant during early exceptions.

Test signals: Early boot logs with and without `earlyprintk`, `ignore_loglevel`, `bootdebug`, and timestamp config; `%pS` symbol resolution in program-check output; ring-buffer wrap tests; and format-string coverage for width, padding, signed values, and unsupported specifiers.

Source read size: 299 lines, complete file reviewed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/boot/printk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/boot/sclp_early_core.c -->
# sources/distributed-fs/ceph-client/arch/s390/boot/sclp_early_core.c

Purpose: Adapts the common SCLP early core implementation for the s390 boot decompressor and supplies a statically allocated early SCCB buffer.

Important APIs/types/functions: Includes `../../../drivers/s390/char/sclp_early_core.c`, defines page-aligned static `__sclp_early_sccb[EXT_SCCB_READ_SCP]`, and exports `sclp_early_setup_buffer()`.

Control flow: `sclp_early_setup_buffer()` passes the boot-local SCCB buffer to `sclp_early_set_buffer()`. All other SCLP early behavior comes from the included common driver source.

State and persistence: The SCCB buffer is static boot memory and must remain page-aligned and below 2GB, as required by SCLP early calls.

Dependencies and integration points: Used by startup and printk paths for SCLP reads, machine feature detection, memory info, and early console output.

Risks: If the included driver source adds dependencies unavailable in the boot environment, this wrapper can break. Buffer size, alignment, and addressability are firmware ABI requirements.

Test signals: Early SCLP read-info/storage-info calls, early console output, and builds after changes to the common SCLP early driver.

Source read size: 11 lines, complete file reviewed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/boot/sclp_early_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/boot/stackprotector.c -->
# sources/distributed-fs/ceph-client/arch/s390/boot/stackprotector.c

Purpose: Pulls the s390 kernel stack protector implementation into the boot build with a boot-specific logging prefix.

Important APIs/types/functions: Defines `boot_fmt(fmt) "stackprot: " fmt` and includes `../kernel/stackprotector.c`. Local behavior is inherited from the shared kernel implementation, including early application from `startup_kernel()`.

Control flow: The shared implementation is compiled into the decompressor and invoked by startup after alternatives and bootdata are prepared.

State and persistence: Stack protector state belongs to the included implementation and the vmlinux metadata it patches or initializes.

Dependencies and integration points: Integrated by `startup.c` through `stack_protector_apply_early(text_lma)`. Depends on the included kernel file remaining compatible with boot-only logging and memory access.

Risks: Stack protector setup is security-sensitive and runs before the normal kernel. Offset mismatches in vmlinux metadata or unsupported dependencies in the included file could leave canaries unapplied or corrupt early text/data.

Test signals: `CONFIG_STACKPROTECTOR` s390 builds, early boot with canary patching enabled, and inspection of patched stack-protector ranges after KASLR relocation.

Source read size: 6 lines, complete file reviewed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/boot/stackprotector.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/boot/startup.c -->
# sources/distributed-fs/ceph-client/arch/s390/boot/startup.c

Purpose: Orchestrates the s390 boot decompressor after the low-level startup code: machine/facility detection, memory discovery, KASLR layout selection, kernel deployment, relocation, page-table construction, bootdata copy, alternatives, stack protector setup, and final jump into the decompressed kernel.

Important APIs/types/functions: Exports preserved bootdata such as `vm_layout`, `__abs_lowcore`, `__memcpy_real_area`, `VMALLOC_START/END`, `MODULES_VADDR/END`, `vmemmap`, `max_mappable`, no-execute masks, TOD state, facility list, and `oldmem_data`. Key functions include `startup_kernel()`, `detect_machine_type()`, `detect_facilities()`, `setup_ident_map_size()`, `setup_kernel_memory_layout()`, `rescue_initrd()`, `copy_bootdata()`, `kaslr_adjust_relocs()`, `kaslr_adjust_got()`, and `kaslr_adjust_vmlinux_info()`.

Control flow: `startup_kernel()` initializes lowcore state, stores IPL parameters, queries ultravisor info, parses command line, reserves decompressor/initrd memory, discovers IPL report and facilities, computes memory limits and virtual layout, sets usable physical memory, detects online ranges, copies IPL certificates, rescues initrd if needed, chooses physical kernel and amode31 locations, deploys the kernel, shrinks decompressor reservation, clears BSS, applies relocations/GOT adjustment, builds vmem, dumps reservations, copies bootdata to the relocated kernel image, applies alternatives and stack protector changes, records the KASLR physical offset in lowcore, and jumps with DAT enabled.

State and persistence: This file is the primary producer of bootdata-preserved runtime layout state. It mutates lowcore, `vmlinux` metadata offsets, KASLR offsets, physical reservations, virtual layout addresses, facility masks, and oldmem/crash-dump limits.

Dependencies and integration points: Integrates nearly every boot subsystem: IPL parsing, SCLP, DIAG feature detection, CMMA, protected virtualization, physmem allocation, KASLR, vmem setup, decompressor metadata, alternatives, stack protector, kdump, initrd, KASAN/KMSAN layout, and the final `jump_to_kernel()` trampoline.

Risks: Ordering is critical and documented in the source. Relocations must follow BSS clearing but precede vmem setup; bootdata copy must follow vmem; physical KASLR offsets must preserve large-page alignment relation to virtual offsets. Incorrect identity-map sizing can make memory unreachable or overlap vmemmap/fixmap/modules/vmalloc. Crash dump and protected virtualization paths intentionally disable or constrain KASLR and memory layout.

Test signals: Full s390 boot matrix with compressed/uncompressed kernels, KASLR on/off, KASAN/KMSAN, initrd relocation, crash dump, stand-alone dump, protected virtualization host/guest, PCI/TX/vector facilities, and low-memory stress. Objdump/linker metadata checks for vmlinux info offsets are also valuable.

Source read size: 649 lines, complete file reviewed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/boot/startup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/boot/string.c -->
# sources/distributed-fs/ceph-client/arch/s390/boot/string.c

Purpose: Provides string and memory helpers for the boot decompressor by including s390 library string code and locally implementing a small set of common helpers needed before the full kernel runtime exists.

Important APIs/types/functions: Includes `../lib/string.c` with sanitizer config macros undefined, and defines `strncmp()`, `sized_strscpy()`, `memset64()`, `skip_spaces()`, `strim()`, `simple_strtoull()`, `simple_strtol()`, and `kstrtobool()`.

Control flow: Numeric parsing uses `simple_guess_base()` for 0/0x prefixes, consumes valid digits until the base is exceeded, and optionally returns the end pointer. `strim()` trims trailing whitespace then returns the first non-space byte. `kstrtobool()` recognizes y/Y/1, n/N/0, on, and off.

State and persistence: No persistent state exists.

Dependencies and integration points: Used by command-line parsing, boot printk formatting, symbol parsing, vmem/linker metadata helpers, and included library routines. Sanitizer macros are explicitly disabled because the decompressor cannot use normal KASAN/KMSAN runtime support.

Risks: These are intentionally small substitutes, not full libc/kernel equivalents. `simple_strtoull()` does not detect overflow. `kstrtobool()` checks only the beginning of accepted strings. Changes in included `../lib/string.c` can affect boot code assumptions.

Test signals: Boot command-line parsing for numeric values and booleans, printk symbol parsing, whitespace trimming, and sanitizer-enabled builds.

Source read size: 168 lines, complete file reviewed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/boot/string.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/boot/trampoline.S -->
# sources/distributed-fs/ceph-client/arch/s390/boot/trampoline.S

Purpose: Provides the final boot trampoline symbol used to enter the decompressed kernel with a supplied PSW.

Important APIs/types/functions: Defines `SYM_CODE_START(jump_to_kernel)` and `SYM_CODE_END(jump_to_kernel)`. The implementation executes `lpswe 0(%r2)`.

Control flow: The caller passes a pointer to a PSW in register 2 according to the s390 calling convention. The trampoline loads that PSW and never returns. It is intentionally separate from `__load_psw()` so GDB's `lx-symbols` breakpoint behavior does not collide with this transition.

State and persistence: No state is stored; CPU execution state changes to the loaded PSW.

Dependencies and integration points: Called from `startup_kernel()` after page tables, bootdata, alternatives, and stack protector setup are complete. It depends on the PSW structure layout and s390 linkage macros.

Risks: Any calling convention mismatch or invalid PSW causes immediate boot failure. The symbol name matters for debugger behavior.

Test signals: Successful transition from decompressor to kernel entry with DAT enabled, debugger breakpoint behavior, and objdump validation of the single `lpswe` sequence.

Source read size: 9 lines, complete file reviewed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/boot/trampoline.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/boot/uv.c -->
# sources/distributed-fs/ceph-client/arch/s390/boot/uv.c

Purpose: Queries ultravisor capabilities during early boot and sanitizes protected virtualization host/guest flags before the kernel proper starts.

Important APIs/types/functions: Exports bootdata-preserved `prot_virt_guest`, `prot_virt_host`, and `struct uv_info uv_info`. Public functions are `uv_query_info()`, `adjust_to_uv_max()`, and `sanitize_prot_virt_host()`. Internal helper `is_prot_virt_host_capable()` enforces host eligibility.

Control flow: `uv_query_info()` requires facility 158, issues `UVC_CMD_QUI`, tolerates `UVC_RC_MORE_DATA`, copies supported ultravisor limits and feature indications into `uv_info` when KVM is enabled, and marks protected-virtualization guest support if set/remove shared-access calls are present. `adjust_to_uv_max()` constrains virtual layout limits for protected-virtualization hosts. `sanitize_prot_virt_host()` clears host mode unless command line, hardware, non-guest, non-kdump, and non-stand-alone-dump conditions are all satisfied.

State and persistence: `uv_info` and protected-virtualization flags are preserved boot data consumed by later s390 kernel and KVM code. The file also reads `oldmem_data` and IPL dump state.

Dependencies and integration points: Called early from `startup_kernel()` before layout decisions and again indirectly through `setup_kernel_memory_layout()` via `adjust_to_uv_max()`. Depends on facility bits, UVC calling ABI, KVM config, IPL dump detection, and crash dump state.

Risks: Incorrect ultravisor limits can place vmalloc/modules above secure storage addressability. Protected-virtualization mode must be disabled for kdump and stand-alone dump. The query intentionally ignores some extra data, so future UV fields require explicit copy support.

Test signals: Protected guest and protected host boots, KVM-enabled builds, facility-158 absent machines, kdump/stand-alone dump boots, and secure storage limit layout checks.

Source read size: 88 lines, complete file reviewed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/boot/uv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/boot/uv.h -->
# sources/distributed-fs/ceph-client/arch/s390/boot/uv.h

Purpose: Declares the small boot-local ultravisor helper API used by s390 startup and layout code.

Important APIs/types/functions: Declares `adjust_to_uv_max()`, `sanitize_prot_virt_host()`, and `uv_query_info()`.

Control flow: Header only; no runtime control flow.

State and persistence: Header only; persistent state is defined in `uv.c`.

Dependencies and integration points: Included by `startup.c` and `uv.c` to share ultravisor boot declarations without exposing unrelated kernel UV internals.

Risks: Missing declarations here will surface as boot build issues. Signature drift would break early layout and protected-virtualization setup.

Test signals: s390 boot builds with protected virtualization configs and compilation after UV helper signature changes.

Source read size: 9 lines, complete file reviewed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/boot/uv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/boot/version.c -->
# sources/distributed-fs/ceph-client/arch/s390/boot/version.c

Purpose: Builds the boot-visible kernel version string used in early diagnostics.

Important APIs/types/functions: Defines `const char kernel_version[]` from generated `UTS_RELEASE`, `LINUX_COMPILE_BY`, `LINUX_COMPILE_HOST`, and `UTS_VERSION`.

Control flow: No runtime logic; the string is compiled into the boot image.

State and persistence: `kernel_version` is read by boot fault and OOM diagnostics.

Dependencies and integration points: Used by `pgm_check.c` and `physmem_info.c` for early crash/OOM reporting. Depends on generated version headers.

Risks: If generated headers are unavailable or inconsistent, boot diagnostics lose version fidelity or the build fails.

Test signals: Build-time generation of UTS headers and early fault/OOM logs containing the expected version string.

Source read size: 8 lines, complete file reviewed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/boot/version.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/boot/vmem.c -->
# sources/distributed-fs/ceph-client/arch/s390/boot/vmem.c

Purpose: Constructs the initial s390 kernel address space during decompression, including identity/direct mappings, kernel image mapping, lowcore mappings, invalid user ASCE, direct-map page counters, and optional KASAN shadow mappings.

Important APIs/types/functions: Defines bootdata-preserved `s390_invalid_asce` and optionally `direct_pages_count[]`. Key API is `setup_vmem(kernel_start, kernel_end, asce_limit)`. Internal machinery includes `enum populate_mode`, `pgtable_populate()`, `pgtable_p4d/pud/pmd/pte_populate()`, `boot_crst_alloc()`, `boot_pte_alloc()`, `resolve_pa_may_alloc()`, large-page helpers, and KASAN shadow helpers.

Control flow: `setup_vmem()` marks all online pages no-DAT before allocating page tables, temporarily switches `init_mm.pgd` to the physical `swapper_pg_dir`, chooses region-table type from `asce_limit`, initializes swapper and invalid page directories, maps lowcore first with 4K pages, then usable identity ranges, kernel text/data excluding the `TEXT_OFFSET` hole, amode31 direct region, absolute lowcore, and a deliberately invalid memcpy-real page. KASAN builds additionally populate mapped, zero, and shallow shadow ranges. Finally it loads kernel/user ASCEs into lowcore and control registers and restores `init_mm.pgd`.

State and persistence: Produces persistent page tables in physical memory allocated as `RR_VMEM`, updates page DAT attributes, direct-map counters, `memcpy_real_ptep`, lowcore ASCE fields, `s390_invalid_asce`, and `init_mm.context.asce`.

Dependencies and integration points: Called from `startup_kernel()` after relocations. Depends on `physmem_info`, `vmlinux` metadata offsets, s390 page-table macros, EDAT1/EDAT2 facilities, KASAN metadata, lowcore relocation, identity-base selection, and absolute lowcore helpers.

Risks: Page-table construction is architecture-critical. Large-page eligibility must match CPUID facilities and alignment; mapping lowcore after identity mapping could accidentally create a large page at zero; invalid `POPULATE_NONE` mapping is intentional for memcpy-real setup. KASAN zero-shadow sharing must not be overwritten by later population. Any mismatch between physical and virtual vmlinux offsets corrupts kernel entry.

Test signals: Boots with 3-level and 4-level paging, EDAT1/EDAT2 on/off, KASAN enabled, memory holes, relocated lowcore, randomized identity base, and direct-map page count validation. Page-table dumps and early fault injection around unmapped memcpy-real area are useful.

Source read size: 556 lines, complete file reviewed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/boot/vmem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/boot/vmlinux.lds.S -->
# sources/distributed-fs/ceph-client/arch/s390/boot/vmlinux.lds.S

Purpose: Linker script for the s390 boot/decompressor image. It fixes boot section layout, embeds compressed vmlinux and metadata, defines decompressor symbols, stores relocation tables, and asserts that forbidden dynamic relocation/linkage sections remain absent.

Important APIs/types/functions: Defines output format/architecture, entry `startup`, sections `.ipldata`, `.head.text`, `.parmarea`, `.text`, `.rodata`, exception table, `.got`, notes, `.data`, `BOOT_DATA`, `BOOT_DATA_PRESERVED`, decompressor `.bss` and stacks, `.vmlinux.info`, `.decompressor.syms`, `_decompressor_end`, `.vmlinux.relocs`, `.rodata.compressed`, `.sb.trailer`, and discard/assertion sections.

Control flow: Link-time only. The script positions the IPL header/startup areas, collects boot code/data, records metadata consumed by `startup.c` and `printk.c`, aligns compressed or uncompressed payload placement, adds a secure-boot trailer, and rejects unexpected PLT or dynamic relocation content.

State and persistence: Produces linker symbols such as `_stack_start/_end`, `_dump_info_stack_start/_end`, `_vmlinux_info`, `_decompressor_syms_start/_end`, `_decompressor_end`, `__vmlinux_relocs_64_start/_end`, `_compressed_start/_end`, and `_end`.

Dependencies and integration points: Consumed by `startup.c`, `printk.c`, `pgm_check.c`, decompressor entry assembly, vmlinux info generation, secure boot tooling, and relocation adjustment logic.

Risks: Section order and alignment are ABI-like. The `.vmlinux.info` layout must match `struct vmlinux_info`; relocation sections must be available until after KASLR relocation; `.sb.trailer` must not overwrite compressed data. Assertions guard against runtime relocations that the decompressor cannot process.

Test signals: Linker map inspection, booting compressed and uncompressed kernels, secure boot trailer validation, relocation table bounds checks, and build failures when unexpected `.plt` or `.rela.dyn` content appears.

Source read size: 173 lines, complete file reviewed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/boot/vmlinux.lds.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/crypto/Kconfig -->
# sources/distributed-fs/ceph-client/arch/s390/crypto/Kconfig

Purpose: Declares user-visible Kconfig options for s390 CPU-accelerated crypto algorithms.

Important APIs/types/functions: Defines menu "Accelerated Cryptographic Algorithms for CPU (s390)", `config CRYPTO_AES_S390`, and `config CRYPTO_HMAC_S390`. AES selects `CRYPTO_SKCIPHER`; HMAC selects `CRYPTO_HASH`.

Control flow: Kconfig-time only. These options control whether corresponding architecture crypto modules can be built and describe the hardware generation support for AES modes and SHA2 HMAC.

State and persistence: No runtime state; selections affect build configuration and module availability.

Dependencies and integration points: Integrated with `arch/s390/crypto/Makefile` and kernel crypto API registration in `aes_s390.c` and `hmac_s390.c`. Protected-key options used by `paes_s390.c` and `phmac_s390.c` are controlled elsewhere but built in the same directory.

Risks: Missing selects can produce link/build failures or unavailable algorithms. Help text must match actual CPACF capability checks in implementation files.

Test signals: Kconfig matrix builds for built-in/module/disabled AES and HMAC, and runtime `crypto_alg` availability matching selected options and CPU support.

Source read size: 33 lines, complete file reviewed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/crypto/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/crypto/Makefile -->
# sources/distributed-fs/ceph-client/arch/s390/crypto/Makefile

Purpose: Maps s390 crypto Kconfig symbols to objects in the architecture crypto directory.

Important APIs/types/functions: Builds `aes_s390.o`, `paes_s390.o`, `prng.o`, `hmac_s390.o`, `phmac_s390.o`, and always builds `arch_random.o`.

Control flow: Build-time only; object inclusion follows `CONFIG_CRYPTO_AES_S390`, `CONFIG_CRYPTO_PAES_S390`, `CONFIG_S390_PRNG`, `CONFIG_CRYPTO_HMAC_S390`, and `CONFIG_CRYPTO_PHMAC_S390`.

State and persistence: No runtime state.

Dependencies and integration points: Ties Kconfig to CPACF-backed crypto drivers and the always-present arch random static-key/counter definitions.

Risks: Incorrect object mapping silently removes accelerated algorithms or links drivers into unsupported builds.

Test signals: s390 crypto config matrix builds and module autoload/alias checks for AES, PAES, HMAC, PHMAC, PRNG, and arch random support.

Source read size: 11 lines, complete file reviewed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/crypto/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/crypto/aes_s390.c -->
# sources/distributed-fs/ceph-client/arch/s390/crypto/aes_s390.c

Purpose: Implements CPACF-accelerated clear-key AES algorithms for s390: ECB, CBC, CTR, XTS, full-XTS, and GCM AEAD.

Important APIs/types/functions: Uses `struct s390_aes_ctx`, `struct s390_xts_ctx`, and `struct gcm_sg_walk`; registers `skcipher_alg` instances for `ecb(aes)`, `cbc(aes)`, `ctr(aes)`, `xts(aes)`, and `__xts(aes)`, plus `aead_alg gcm(aes)`. Key functions include `*_set_key()`, `*_crypt()`, fallback init/exit helpers, CTR block helpers, GCM scatterlist walkers, `gcm_aes_crypt()`, `aes_s390_register_skcipher()`, `aes_s390_init()`, and `aes_s390_fini()`.

Control flow: Module init queries CPACF KM, KMC, KMCTR, and KMA masks, registering only algorithms with matching hardware functions. ECB/CBC/CTR/XTS paths validate keys, choose function codes by key length, and run CPACF instructions over skcipher walks, falling back where needed. GCM builds the CPACF KMA parameter block, walks AAD and payload scatterlists, sets last-AAD/last-payload flags when final chunks are reached, writes tags on encrypt, and compares tags on decrypt.

State and persistence: Persistent module state includes CPACF function masks, the global CTR block page protected by `ctrblk_lock`, registered algorithm pointers, and per-transform AES key material/function codes. GCM parameter blocks and tags are stack-local and explicitly zeroed.

Dependencies and integration points: Integrates with the Linux crypto skcipher/AEAD APIs, CPACF instruction wrappers, scatterwalk/skcipher walk helpers, fallback crypto allocations, module CPU feature matching, and crypto selftests.

Risks: Scatterlist boundary handling in GCM is delicate because CPACF requires block-size progress and correct final flags. CTR uses a shared buffer and mutex. XTS key validation and fallback naming must match crypto API expectations. Tag comparison must remain constant-time via `crypto_memneq()`.

Test signals: Kernel crypto selftests for all AES modes and key sizes, GCM AAD-only/empty-payload/tag-failure cases, scatterlist fragmentation tests, FIPS mode, CPU masks with partial CPACF support, and module unload cleanup.

Source read size: 1046 lines, complete file reviewed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/crypto/aes_s390.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/crypto/arch_random.c -->
# sources/distributed-fs/ceph-client/arch/s390/crypto/arch_random.c

Purpose: Defines shared s390 architecture random-number availability and accounting state.

Important APIs/types/functions: Defines `DEFINE_STATIC_KEY_FALSE(s390_arch_random_available)` and exported `atomic64_t s390_arch_random_counter`.

Control flow: No local runtime functions; other s390 arch-random code toggles or consumes the static key and counter.

State and persistence: The static key records whether architectural random support is available. The exported atomic counter tracks arch-random usage or output accounting for other code.

Dependencies and integration points: Included unconditionally by the crypto Makefile. Depends on `asm/archrandom.h`, CPACF headers, static keys, atomics, and Linux random infrastructure.

Risks: This file is only state definition; mismatched extern declarations elsewhere would break linking. Counter semantics must remain consistent with consumers.

Test signals: s390 builds with arch random support, symbol export checks, and runtime toggling/usage through the arch random implementation.

Source read size: 20 lines, complete file reviewed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/crypto/arch_random.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/crypto/hmac_s390.c -->
# sources/distributed-fs/ceph-client/arch/s390/crypto/hmac_s390.c

Purpose: Implements CPACF-accelerated clear-key HMAC-SHA224/256/384/512 for the synchronous hash API.

Important APIs/types/functions: Defines `struct s390_hmac_ctx`, `union s390_kmac_gr0`, and `struct s390_kmac_sha2_ctx`. Key functions are `hash_data()`, `hash_key()`, `s390_hmac_sha2_setkey()`, `s390_hmac_sha2_init()`, `s390_hmac_sha2_update()`, `s390_hmac_sha2_finup()`, `s390_hmac_sha2_digest()`, export/import helpers, and module init/exit over `s390_hmac_algs[]`.

Control flow: Init requires KLMD SHA-256 and SHA-512 support for selftest/hash-key support, then registers only HMAC variants with matching KMAC function codes. Setkey hashes overlong keys, creates inner/outer padded key blocks, and stores them in transform context. Init seeds descriptor state from ipad, update streams data through KMAC state, and final/finup produces the digest using opad state.

State and persistence: Per-transform context stores ipad/opad-derived state and digest metadata. Per-request descriptor state holds partial SHA2/KMAC state across update/final. Registered flags track cleanup ordering.

Dependencies and integration points: Integrates with `crypto_shash`, CPACF KMAC/KLMD wrappers, SHA2 state sizes, module CPU feature matching, and crypto selftests.

Risks: Export/import compatibility must preserve in-progress HMAC state exactly. Key normalization and block-size handling differ across SHA256-family and SHA512-family variants. Registration requires both KLMD families even if only some HMAC variants are used.

Test signals: Crypto manager HMAC vectors for SHA224/256/384/512, incremental update/export/import tests, overlong and zero-length keys, partial CPU feature masks, and module unload tests.

Source read size: 426 lines, complete file reviewed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/crypto/hmac_s390.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/crypto/paes_s390.c -->
# sources/distributed-fs/ceph-client/arch/s390/crypto/paes_s390.c

Purpose: Implements s390 protected-key AES algorithms for ECB, CBC, CTR, and XTS through the async crypto-engine skcipher API.

Important APIs/types/functions: Defines `struct paes_protkey`, `struct s390_paes_ctx`, `struct s390_pxts_ctx`, mode parameter/request structs, global CPACF masks, `paes_crypto_engine`, `ctrblk`, and module parameter `clrkey`. Key helpers are `make_clrkey_token()`, `paes_ctx_setkey()`, `pxts_ctx_setkey()`, `convert_key()`, `paes_convert_key()`, `pxts_convert_key()`, per-mode setkey/do_crypt/crypt/init/exit/do_one_request functions, and `paes_s390_init()/fini()`.

Control flow: Module init registers a `/dev/paes` pseudo miscdevice, starts a crypto engine, queries KM/KMC/KMCTR masks, and registers each protected-key algorithm only if hardware supports it. Setkey accepts protected-key tokens, and optionally clear keys when `clrkey=Y`, converting them through pkey APIs into protected keys. Requests are enqueued to the crypto engine and executed by per-mode `do_one_request()` callbacks. Each mode converts/refetches protected keys as needed and invokes CPACF functions; XTS supports full-key and two-key protected forms.

State and persistence: Module state includes the crypto engine, miscdevice, CPACF masks, shared CTR block page/mutex, and registered algorithm state. Transform contexts persist protected key blobs, key type/length, and fallback/conversion status; request contexts hold mode parameters and asynchronous completion state.

Dependencies and integration points: Integrates with s390 pkey token conversion/verification, CPACF PAES/PXTS functions, Linux crypto engine, skcipher API, miscdevice core, and crypto selftests.

Risks: Protected-key validity can change, so conversion and retry handling are security and correctness sensitive. Allowing clear-key input is gated by a module parameter and must remain explicit. Async engine lifecycle must be unwound correctly on partial registration failure. CTR shared buffer locking and XTS key-size/token interpretation are high-risk areas.

Test signals: Crypto selftests for PAES modes with protected tokens, clear-key-token mode when enabled, invalid/stale pkey token errors, async request cancellation/completion, partial CPACF support, module load/unload, and pkey subsystem integration tests.

Source read size: 1729 lines, complete file reviewed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/crypto/paes_s390.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/crypto/phmac_s390.c -->
# sources/distributed-fs/ceph-client/arch/s390/crypto/phmac_s390.c

Purpose: Implements asynchronous protected-key HMAC-SHA224/256/384/512 using CPACF PHMAC/KMAC functions and the Linux crypto engine.

Important APIs/types/functions: Defines `struct hash_walk_helper`, `struct phmac_protkey`, `struct phmac_tfm_ctx`, `union kmac_gr0`, `struct kmac_sha2_ctx`, `enum async_op`, `struct phmac_req_ctx`, and `struct hmac_clrkey_token`. Key functions include hash-walk helpers, `hash_key()`, `make_clrkey_token()`, `phmac_tfm_ctx_setkey()`, `convert_key()`, `phmac_convert_key()`, `phmac_kmac_update()`, `phmac_kmac_final()`, request operations `phmac_init/update/final/finup/digest`, `phmac_setkey()`, export/import, tfm init/exit, `phmac_do_one_request()`, and module init/exit.

Control flow: Init verifies SHA KLMD support for selftests, registers a `/dev/phmac` miscdevice, starts a crypto engine, and registers variants with available PHMAC KMAC subfunctions. Setkey accepts protected keys or optional clear-key tokens, normalizes overlong keys, converts to protected form, and prepares ipad/opad state. Async update/final/digest operations store request context and are completed by the crypto engine, which walks scatterlists and feeds CPACF KMAC/PHMAC.

State and persistence: Per-transform context stores protected key material, converted state, and digest sizes. Per-request context tracks the current async operation, hash state, partial scatterlist walk, and result buffer. Module state includes the engine, miscdevice, registered flags, and `clrkey` policy.

Dependencies and integration points: Depends on pkey APIs, CPACF KMAC/PHMAC/KLMD, ahash crypto-engine APIs, scatterlist kmap handling, miscdevice core, and crypto selftests.

Risks: Async hash continuation and export/import must maintain exact state across split updates. Protected-key conversion failures must not leak clear key material. Scatterlist walking in sleep/non-sleep contexts is subtle. Engine teardown must not race in-flight requests.

Test signals: ahash selftests for PHMAC variants, incremental and one-shot requests, export/import, invalid protected tokens, clear-key parameter coverage, high-fragmentation scatterlists, async completion stress, and module unload under load.

Source read size: 1074 lines, complete file reviewed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/crypto/phmac_s390.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/crypto/prng.c -->
# sources/distributed-fs/ceph-client/arch/s390/crypto/prng.c

Purpose: Provides the legacy s390 `/dev/prandom` interface backed by CPACF TDES PRNG or SHA512 PRNO DRNG, with optional TRNG seeding, FIPS conditional tests, sysfs attributes, reseeding controls, and module parameters.

Important APIs/types/functions: Defines module parameters `mode`, `chunksize`, and `reseed_limit`; structs `prng_ws_s`, `prno_ws_s`, and `prng_data_s`; global `prng_data`, `trng_available`, and `prng_errorflag`. Key functions include `generate_entropy()`, TDES seed/instantiate/read/deinstantiate paths, SHA512 selftest/instantiate/reseed/generate/read paths, `prng_open()`, sysfs show/store handlers, and `prng_init()/exit()`.

Control flow: Init requires KMC PRNG support, detects TRNG and SHA512 PRNO support, selects SHA512 unless TDES is forced or SHA512 unavailable, validates chunk/reseed limits, instantiates state, and registers the matching miscdevice. SHA512 mode runs a NIST-vector selftest, seeds from TRNG or generated entropy plus TOD nonce, optionally records a previous block for FIPS conditional testing, reseeds when the PRNO reseed counter exceeds the limit, and serves reads in locked chunks. TDES mode mixes generated entropy into the KMC PRNG parameter block and serves reads with FIPS duplicate-block checks.

State and persistence: Persistent module state includes PRNG workspace, output buffer, previous-block buffer in FIPS mode, byte counter, mutex, mode, chunk size, reseed limit, and error flag. Sysfs exposes mode, strength, chunksize, byte counter, error flag, and reseed controls.

Dependencies and integration points: Integrates with CPACF KMC/PRNO/TRNG, miscdevice registration, sysfs device attributes, FIPS mode, user-copy helpers, TOD clock, and module CPU feature matching.

Risks: This interface is legacy and security-sensitive. Entropy estimation differs between TRNG and generated entropy paths. FIPS duplicate-block testing depends on chunk sizing. User reads must hold the mutex around shared state. Reseed controls and error flags must not mask failed selftests or generation failures.

Test signals: Module load in SHA512, TDES-forced, and unsupported modes; NIST selftest success/failure injection; FIPS conditional self-test; concurrent reads; sysfs reseed and reseed_limit behavior; byte counter accounting; and miscdevice cleanup.

Source read size: 910 lines, complete file reviewed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/crypto/prng.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/hypfs/Makefile -->
# sources/distributed-fs/ceph-client/arch/s390/hypfs/Makefile

Purpose: Builds the s390 hypervisor filesystem core, debugfs diagnostic files, and optional mounted filesystem view.

Important APIs/types/functions: Adds `hypfs_dbfs.o`, `hypfs_diag.o`, `hypfs_diag0c.o`, `hypfs_sprp.o`, and `hypfs_vm.o` for `CONFIG_S390_HYPFS`; adds `hypfs_diag_fs.o`, `hypfs_vm_fs.o`, and `inode.o` for `CONFIG_S390_HYPFS_FS`.

Control flow: Build-time only. The debugfs and diagnostic collection core can be built independently of the filesystem front end.

State and persistence: No runtime state.

Dependencies and integration points: Coordinates object inclusion for the public declarations in `hypfs.h`, diag-specific helpers, z/VM helpers, SPRP ioctl support, and mounted hypfs inode implementation.

Risks: Missing an object can produce unresolved symbols only for certain config combinations, especially the inline `IS_ENABLED(CONFIG_S390_HYPFS_FS)` wrappers.

Test signals: Build matrix for `CONFIG_S390_HYPFS` and `CONFIG_S390_HYPFS_FS`, including built-in and module-like combinations.

Source read size: 14 lines, complete file reviewed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/hypfs/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/hypfs/hypfs.h -->
# sources/distributed-fs/ceph-client/arch/s390/hypfs/hypfs.h

Purpose: Central header for s390 hypfs, defining filesystem modes, exported creation helpers, diagnostic init/exit interfaces, and the common debugfs file callback model.

Important APIs/types/functions: Defines `REG_FILE_MODE`, `UPDATE_FILE_MODE`, and `DIR_MODE`; declares `hypfs_mkdir()`, `hypfs_create_u64()`, `hypfs_create_str()`, LPAR and VM init/create/exit functions, `hypfs_diag0c_init/exit()`, `hypfs_sprp_init/exit()`, and `hypfs_fs_init()`. Defines `struct hypfs_dbfs_data` and `struct hypfs_dbfs_file`.

Control flow: Header wrappers use `IS_ENABLED(CONFIG_S390_HYPFS_FS)` so the core can call `hypfs_fs_init()` regardless of whether the mounted filesystem view is compiled.

State and persistence: `struct hypfs_dbfs_file` persists per-debugfs-file metadata, callback pointers, lock, and dentry. `struct hypfs_dbfs_data` is per-read generated data.

Dependencies and integration points: Shared by all hypfs implementation files and by `inode.c`. It bridges diagnostic producers and the common debugfs reader in `hypfs_dbfs.c`.

Risks: Callback contracts are important: `data_create()` must set buffer, free pointer, and size consistently; `data_free()` must match allocation method. Incorrect mode constants affect hypfs file permissions.

Test signals: Build checks across config variants, debugfs file reads, mounted hypfs tree creation, and callback allocation/free fault injection.

Source read size: 82 lines, complete file reviewed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/hypfs/hypfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/hypfs/hypfs_dbfs.c -->
# sources/distributed-fs/ceph-client/arch/s390/hypfs/hypfs_dbfs.c

Purpose: Provides the common debugfs interface for hypfs diagnostic data and initializes all hypfs diagnostic backends.

Important APIs/types/functions: Defines global `dbfs_dir`, helpers `hypfs_dbfs_data_alloc()`, `hypfs_dbfs_data_free()`, `dbfs_read()`, `dbfs_ioctl()`, file operations `dbfs_ops` and `dbfs_ops_ioctl`, exported `hypfs_dbfs_create_file()` and `hypfs_dbfs_remove_file()`, and init function `hypfs_dbfs_init()`.

Control flow: A debugfs read at offset 0 locks the file callback object, allocates a `hypfs_dbfs_data`, invokes the backend `data_create()`, unlocks, copies generated bytes to userspace with `simple_read_from_buffer()`, then frees data. Ioctls are serialized by the same mutex. Init creates `/sys/kernel/debug/s390_hypfs`, initializes DIAG 204/224, z/VM DIAG 2FC, SPRP DIAG 304, DIAG 0C, and optional hypfs filesystem support, unwinding in reverse on failure.

State and persistence: The global debugfs directory and each backend dentry persist after init. Per-file mutexes serialize collection and ioctl mutation.

Dependencies and integration points: Integrates with Linux debugfs, lockdown policy, security `LOCKDOWN_DEBUGFS`, backend callback structs in diag/vm/sprp files, and optional filesystem init.

Risks: `hypfs_dbfs_create_file()` exposes ioctl operations only when lockdown allows it, which is security-critical for DIAG 304. Read callbacks generate whole snapshots per read; large buffers rely on backend allocation discipline. Init failure unwinding must match successful steps.

Test signals: Debugfs reads for diag_204/2fc/0c/304, lockdown mode hiding ioctls, init failure injection for each backend, concurrent readers, and optional filesystem config tests.

Source read size: 128 lines, complete file reviewed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/hypfs/hypfs_dbfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/hypfs/hypfs_diag.c -->
# sources/distributed-fs/ceph-client/arch/s390/hypfs/hypfs_diag.c

Purpose: Probes and stores LPAR hypervisor DIAG 204 data and exposes raw extended DIAG 204 snapshots through debugfs.

Important APIs/types/functions: Maintains `diag204_store_sc`, `diag204_info_type`, `diag204_buf`, and `diag204_buf_pages`. Public functions are `diag204_get_info_type()`, `diag204_get_buffer()`, `diag204_store()`, `hypfs_diag_init()`, and `hypfs_diag_exit()`. It defines packed debugfs header structs `dbfs_d204_hdr` and `dbfs_d204`.

Control flow: `diag204_probe()` first attempts extended DIAG 204 data with subcode 7, then subcode 6, and falls back to simple subcode 4. Extended mode uses DIAG 204 RSI to size the buffer, then vmallocs a page-aligned area. `diag204_store()` builds the selected subcode, adds BIF when available, and retries on `-EBUSY` unless a signal is pending. Debugfs creation allocates an aligned buffer with a 64-byte header and stores the raw DIAG 204 payload behind it.

State and persistence: Selected DIAG format/subcode and the reusable vmalloc buffer persist for all hypfs diag consumers. The debugfs raw snapshot is generated per read and freed afterward.

Dependencies and integration points: Integrates with `hypfs_diag_fs.c` for mounted filesystem formatting, `hypfs_dbfs.c` for raw debugfs exposure, DIAG 204/224 definitions, vmalloc, scheduling, signal handling, and EBCDIC conversion in consumers.

Risks: The buffer-size path trusts DIAG 204 RSI page counts. Busy retry can be interrupted by signals. Extended-only debugfs file creation means simple-mode machines still rely on filesystem formatting rather than raw debugfs.

Test signals: LPAR systems supporting DIAG 204 subcodes 7, 6, and 4; busy-retry behavior; raw diag_204 debugfs format validation; and mounted hypfs tree creation.

Source read size: 224 lines, complete file reviewed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/hypfs/hypfs_diag.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/hypfs/hypfs_diag.h -->
# sources/distributed-fs/ceph-client/arch/s390/hypfs/hypfs_diag.h

Purpose: Declares shared DIAG 204/224 hypfs helpers and config-gated filesystem formatting hooks.

Important APIs/types/functions: Declares `diag204_get_info_type()`, `diag204_get_buffer()`, `diag204_store()`, `__hypfs_diag_fs_init()`, and `__hypfs_diag_fs_exit()`. Inline wrappers `hypfs_diag_fs_init()` and `hypfs_diag_fs_exit()` call the filesystem hooks only when `CONFIG_S390_HYPFS_FS` is enabled.

Control flow: Header-only config gating; no local runtime logic beyond inline wrappers.

State and persistence: No local state; shared state is in `hypfs_diag.c`.

Dependencies and integration points: Included by DIAG 204 raw and filesystem formatting files. Depends on `asm/diag.h` for `enum diag204_format`.

Risks: Incorrect config gating can create unresolved references or skip required init. Function signature drift breaks diag consumers.

Test signals: Build matrix for `CONFIG_S390_HYPFS_FS` and DIAG formatting initialization/exit.

Source read size: 35 lines, complete file reviewed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/hypfs/hypfs_diag.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/hypfs/hypfs_diag0c.c -->
# sources/distributed-fs/ceph-client/arch/s390/hypfs/hypfs_diag0c.c

Purpose: Exposes z/VM DIAG 0C per-CPU diagnostic data through the hypfs debugfs framework.

Important APIs/types/functions: Defines `diag0c_fn()`, `diag0c_store()`, `dbfs_diag0c_free()`, `dbfs_diag0c_create()`, `dbfs_file_0c`, `hypfs_diag0c_init()`, and `hypfs_diag0c_exit()`. Uses `struct hypfs_diag0c_data`, `struct hypfs_diag0c_entry`, and `struct hypfs_diag0c_hdr` from UAPI/asm hypfs headers.

Control flow: `diag0c_store()` locks the CPU hotplug read side, allocates a vector indexed by possible CPU and a real-storage DMA-capable result structure sized for online CPUs, fills per-online-CPU pointers, runs `diag0c_fn()` on each CPU using `on_each_cpu()`, and returns the collected data. The debugfs create callback adds a TOD timestamp and header length/count before returning the buffer.

State and persistence: No global diagnostic state persists beyond the registered debugfs file. Each read allocates a fresh snapshot.

Dependencies and integration points: Available only on z/VM (`machine_is_vm()`). Integrates with CPU hotplug locking, per-CPU execution, DIAG 0C, hypfs debugfs callbacks, and TOD clock.

Risks: DIAG 0C requires 8-byte alignment and real storage, so allocation flags matter. CPU hotplug must be locked while building and using the CPU vector. `on_each_cpu()` latency affects debugfs reads.

Test signals: z/VM debugfs `diag_0c` reads with CPU hotplug stress, non-z/VM no-op init/exit, per-CPU count/header validation, and allocation failure injection.

Source read size: 124 lines, complete file reviewed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/hypfs/hypfs_diag0c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/hypfs/hypfs_diag_fs.c -->
# sources/distributed-fs/ceph-client/arch/s390/hypfs/hypfs_diag_fs.c

Purpose: Converts LPAR DIAG 204 and DIAG 224 data into the mounted hypfs directory tree.

Important APIs/types/functions: Defines many accessors that abstract simple and extended DIAG 204 formats, including info-block, partition-header, CPU-info, physical-header, and physical-CPU getters. Key functions are `hypfs_create_cpu_files()`, `hypfs_create_lpar_files()`, `hypfs_create_phys_cpu_files()`, `hypfs_create_phys_files()`, `hypfs_diag_create_files()`, `diag224_idx2name()`, `diag224_get_name_table()`, `diag224_delete_name_table()`, `__hypfs_diag_fs_init()`, and `__hypfs_diag_fs_exit()`.

Control flow: Init fetches the DIAG 224 CPU type name table on LPAR machines. `hypfs_diag_create_files()` gets and refreshes the DIAG 204 buffer, creates `/systems`, iterates partition records to create per-LPAR CPU directories and timing/type files, optionally creates physical CPU files when DIAG 204 flags include physical data, then creates `/hyp/type` as "LPAR Hypervisor".

State and persistence: `diag224_cpu_names` is a single DMA-capable page retained until exit. The mounted hypfs tree is reconstructed by the inode layer on update and stores generated file contents as dentries/inodes.

Dependencies and integration points: Uses `hypfs_diag.c` for DIAG 204 storage, `hypfs.h` inode helpers, DIAG 224 for CPU type names, EBCDIC-to-ASCII conversion, and machine type detection.

Risks: Pointer arithmetic over firmware DIAG 204 buffers must match selected simple/extended struct sizes. DIAG 224 index conversion assumes the name table is present and large enough. A historical naming mistake is preserved: `weight_min` actually represents operating CPUs in the z/VM file path, not here.

Test signals: Mounted hypfs on LPAR with simple and extended DIAG 204 data, DIAG 224 unavailable failures, physical CPU section presence/absence, EBCDIC name trimming, and tree update tests.

Source read size: 377 lines, complete file reviewed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/hypfs/hypfs_diag_fs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/hypfs/hypfs_sprp.c -->
# sources/distributed-fs/ceph-client/arch/s390/hypfs/hypfs_sprp.c

Purpose: Provides the hypfs debugfs interface for Set Partition-Resource Parameter operations through DIAG 304.

Important APIs/types/functions: Defines DIAG 304 commands `SET_WEIGHTS`, `QUERY_PRP`, and `SET_CAPPING`; low-level `__hypfs_sprp_diag304()`, counted wrapper `hypfs_sprp_diag304()`, debugfs read callback `hypfs_sprp_create()`, ioctl helper `__hypfs_sprp_ioctl()`, ioctl dispatcher `hypfs_sprp_ioctl()`, `hypfs_sprp_file`, `hypfs_sprp_init()`, and `hypfs_sprp_exit()`.

Control flow: A read allocates one zeroed page, issues DIAG 304 query, and returns the page only when the diagnose return code is 1. The ioctl path requires `CAP_SYS_ADMIN`, copies a `struct hypfs_diag304` from userspace, validates command fields, optionally copies a page of user data for set operations, executes DIAG 304, copies query data back for query commands, and returns the updated control block.

State and persistence: No persistent data except the registered debugfs file. Each read/ioctl uses a temporary page and control block.

Dependencies and integration points: Exposed only when `sclp.has_sprp` is true. Integrated with hypfs debugfs locking, Linux capability checks, debugfs lockdown gating in `hypfs_dbfs.c`, DIAG statistics, SCLP feature discovery, and UAPI `HYPFS_DIAG304`.

Risks: This is a privileged resource-control surface. User command validation, capability checks, and lockdown handling are security-critical. DIAG 304 uses physical addresses, so page allocation and address translation must remain valid.

Test signals: SPRP-capable systems reading `diag_304`, ioctl query/set/capping as root and non-root, lockdown mode blocking ioctl exposure, invalid command validation, and user-copy fault injection.

Source read size: 147 lines, complete file reviewed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/hypfs/hypfs_sprp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/hypfs/hypfs_vm.c -->
# sources/distributed-fs/ceph-client/arch/s390/hypfs/hypfs_vm.c

Purpose: Implements z/VM DIAG 2FC data collection and raw debugfs exposure for hypfs.

Important APIs/types/functions: Defines query strings for local/all guests, global `diag2fc_guest_query`, low-level `diag2fc()`, public `diag2fc_store()` and `diag2fc_free()`, debugfs structs `dbfs_d2fc_hdr` and `dbfs_d2fc`, callback `dbfs_diag2fc_create()`, `dbfs_file_2fc`, `hypfs_vm_init()`, and `hypfs_vm_exit()`.

Control flow: `diag2fc()` builds a parameter list with EBCDIC-converted user and group queries, calls DIAG 2FC, and returns either residual-derived size/count information or a hypervisor return code. `diag2fc_store()` first queries required size, vmallocs size plus optional header offset, then retries until a store succeeds. Init runs only on z/VM, preferring all-guest query if authorized, falling back to local-guest query, then registers raw debugfs `diag_2fc`.

State and persistence: `diag2fc_guest_query` records the authorized query mode for later raw and filesystem reads. Each snapshot is vmalloced and freed per read.

Dependencies and integration points: Used by `hypfs_vm_fs.c` to create the mounted tree and by `hypfs_dbfs.c` for raw debugfs. Depends on z/VM DIAG 2FC, EBCDIC conversion, exception-table guarded inline assembly, TOD timestamps, and machine type detection.

Risks: Authorization failures are represented as `-EACCES`; systems without all-guest authorization must fall back correctly. The size-query/store loop must handle changing guest counts. Raw data format depends on `struct diag2fc_data` layout.

Test signals: z/VM systems with all-guest and local-only privileges, changing guest population during reads, raw `diag_2fc` header validation, and non-z/VM no-op behavior.

Source read size: 142 lines, complete file reviewed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/hypfs/hypfs_vm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/hypfs/hypfs_vm.h -->
# sources/distributed-fs/ceph-client/arch/s390/hypfs/hypfs_vm.h

Purpose: Defines the z/VM DIAG 2FC data model and helper declarations shared by raw debugfs and mounted hypfs formatting code.

Important APIs/types/functions: Defines `DIAG2FC_NAME_LEN`, `struct diag2fc_data`, `struct diag2fc_parm_list`, `diag2fc_store()`, `diag2fc_free()`, and extern `diag2fc_guest_query`.

Control flow: Header only; no runtime control flow.

State and persistence: `struct diag2fc_data` describes persisted snapshot records: CPU times, elapsed time, memory limits/usage/share, physical/logical/virtual CPU counts, CPU weights/samples, and EBCDIC guest name. `diag2fc_guest_query` state is defined in `hypfs_vm.c`.

Dependencies and integration points: Included by `hypfs_vm.c` and `hypfs_vm_fs.c`. The structure layout must match z/VM DIAG 2FC format.

Risks: Layout changes would break hypervisor ABI parsing and raw debugfs consumers. Fields are fixed-width and endian/encoding sensitive.

Test signals: Compile checks for both VM files, raw DIAG 2FC size/count validation, and mounted hypfs value checks against z/VM data.

Source read size: 50 lines, complete file reviewed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/hypfs/hypfs_vm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/hypfs/hypfs_vm_fs.c -->
# sources/distributed-fs/ceph-client/arch/s390/hypfs/hypfs_vm_fs.c

Purpose: Converts z/VM DIAG 2FC records into the mounted hypfs directory tree.

Important APIs/types/functions: Defines helper macro `ATTRIBUTE()`, `hypfs_vm_create_guest()`, and public `hypfs_vm_create_files()`.

Control flow: `hypfs_vm_create_files()` obtains a DIAG 2FC snapshot using the query selected in `hypfs_vm.c`, creates `/hyp/type` as "z/VM Hypervisor", creates `/cpus/count` from logical CPU data, creates `/systems`, and iterates all guest records. `hypfs_vm_create_guest()` converts the guest name from EBCDIC, creates per-guest directories, writes online time, CPU timing/capping/dedication/count/weight attributes, memory min/max/used/share attributes, and scheduler sample counters.

State and persistence: The DIAG 2FC snapshot is temporary and freed after tree creation. The generated hypfs tree persists until the next filesystem update/rebuild.

Dependencies and integration points: Depends on `hypfs_vm.c` collection, `hypfs.h` inode creation helpers, EBCDIC conversion, and mounted hypfs update flow in `inode.c`.

Risks: Field naming is partly ABI-frozen; the source notes `weight_min` is historically misnamed and actually contains operating CPU count. Guest names after trimming must be valid unique directory names. Errors during tree creation must free the snapshot.

Test signals: Mounted hypfs on z/VM with multiple guests, EBCDIC guest-name conversion, CPU/memory/sample value validation against DIAG 2FC, duplicate or blank guest-name handling, and update-path failure injection.

Source read size: 134 lines, complete file reviewed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/hypfs/hypfs_vm_fs.c -->
