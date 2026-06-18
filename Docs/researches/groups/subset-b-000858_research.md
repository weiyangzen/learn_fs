# Research: subset-b-000858

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/compressed/pgtable_64.c -->
# sources/distributed-fs/ceph-client/arch/x86/boot/compressed/pgtable_64.c

Purpose: handles the compressed x86-64 kernel's early switch between 4-level and 5-level paging. It decides whether LA57 is required from command line and CPUID, finds a safe low-memory trampoline placement, copies the trampoline template, builds a temporary top-level page table, calls the trampoline, moves the resulting top page table to the caller-provided page-table buffer, and restores overwritten low memory.

Important APIs and state: exports `configure_5level_paging(struct boot_params *bp, void *pgtable)`. Persistent early state is held in `.data` variables `__pgtable_l5_enabled`, `pgdir_shift`, `ptrs_per_p4d`, and `trampoline_32bit`, because `.bss` is cleared during decompression. `find_trampoline_placement()` uses `boot_params_ptr->e820_table`, EFI loader signatures, EBDA, and BIOS low-memory size. It depends on `trampoline_32bit_src`, `trampoline_ljmp_imm_offset`, and `TRAMPOLINE_32BIT_*` constants from startup assembly.

Control flow: `configure_5level_paging()` sanitizes boot params, checks `no5lvl`, CPUID leaf 7 ECX bit 16, and current CR4.LA57. If the requested mode already matches hardware, it returns after updating the global paging-shape variables. Otherwise it saves a low-memory trampoline buffer, copies code, patches the absolute far-jump immediate, prepares either a new 5-level root pointing at the old CR3 or a copied 4-level root from the current 5-level tree, calls the trampoline, copies the new top-level page to `pgtable`, writes CR3, and restores low memory.

Dependencies and integration: consumed by compressed/head startup before the normal kernel virtual mapping exists. It relies on sanitized boot protocol data, e820 RAM typing, early string helpers, raw CR3/CR4/CPUID helpers, and unencrypted page-table flags (`_PAGE_TABLE_NOENC`) for memory-encrypted guests.

Risks and test signals: placement must never collide with BIOS/EBDA or non-RAM e820 ranges, and `trampoline_32bit` must remain under 4 GiB. Off-by-one or alignment errors can destroy low memory or leave CR3 pointing at an invalid root. Useful tests are booting with and without `no5lvl` on LA57-capable hardware or emulation, EFI and non-EFI boots, SEV/SME guests, and inspection that `__pgtable_l5_enabled`, `pgdir_shift`, and `ptrs_per_p4d` match final CR4.LA57.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/compressed/pgtable_64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/compressed/sbat.S -->
# sources/distributed-fs/ceph-client/arch/x86/boot/compressed/sbat.S

Purpose: embeds SBAT revocation metadata into the compressed kernel image when EFI SBAT support is enabled.

Important APIs and state: this assembly has no callable API. It pushes an allocatable `.sbat` section and includes `CONFIG_EFI_SBAT_FILE` verbatim with `.incbin`.

Control flow: build-time only. The linker script collects `.sbat`, aligns it to a page, and the PE header in `header.S` advertises it as a discardable readable PE section.

Dependencies and integration: depends on Kconfig/build-system definition of `CONFIG_EFI_SBAT_FILE`, `CONFIG_EFI_SBAT`, and the compressed kernel linker script. Integration is with EFI Secure Boot revocation policy, not runtime boot logic.

Risks and test signals: a missing or malformed SBAT file breaks the build or creates incorrect EFI metadata. Test by building with `CONFIG_EFI_SBAT=y`, inspecting the PE section table for `.sbat`, and validating the embedded CSV-like SBAT contents used by shim/firmware tooling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/compressed/sbat.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/compressed/sev-handle-vc.c -->
# sources/distributed-fs/ceph-client/arch/x86/boot/compressed/sev-handle-vc.c

Purpose: provides the compressed-kernel #VC handler used after the GHCB page is available for SEV-ES/SNP guests. It supports the small instruction-emulation subset needed during decompression.

Important APIs and state: exports `do_boot_stage2_vc(struct pt_regs *regs, unsigned long exit_code)` and aliases `sev_insn_decode_init()` to `inat_init_tables`. Local helpers implement instruction decode, memory reads/writes, I/O checks, and stub segment handling for the included shared #VC handler. It includes `inat.c`, `insn.c`, and `coco/sev/vc-shared.c` into the compressed environment.

Control flow: the handler ensures `boot_ghcb` exists via `early_setup_ghcb()`, invalidates it, initializes an emulation context, verifies opcode bytes, dispatches RDTSC/RDTSCP, IOIO, and CPUID exits to shared handlers, advances RIP on success, retries on `ES_RETRY`, and terminates the guest for unsupported or failed exits.

Dependencies and integration: depends on `boot_ghcb`, GHCB setup from `sev.c`, Linux instruction decoder tables, and AMD SEV shared GHCB protocol definitions. It is installed only for early boot, before the full kernel exception and #VC infrastructure is live.

Risks and test signals: the supported exit set is intentionally narrow; new early instructions that can #VC must be added or boot will terminate. Tests are SEV-ES/SNP boots through decompression, CPUID exits using the SNP table, early port I/O, RDTSC handling, and negative tests confirming unsupported exits terminate rather than silently corrupting register state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/compressed/sev-handle-vc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/compressed/sev.c -->
# sources/distributed-fs/ceph-client/arch/x86/boot/compressed/sev.c

Purpose: implements compressed-stage AMD SEV, SEV-ES, and SEV-SNP enablement. It detects SEV capabilities, negotiates GHCB protocol, sets the SME encryption mask, initializes SNP CPUID/SVSM state from the CC blob, accepts or changes SNP page state, and prepares identity mappings required by the uncompressed kernel.

Important APIs and state: exports `sev_enable()`, `sev_get_status()`, `early_setup_ghcb()`, `sev_es_shutdown_ghcb()`, `snp_set_page_private()`, `snp_set_page_shared()`, `snp_accept_memory()`, `snp_check_features()`, `snp_get_unsupported_features()`, `sev_prep_identity_maps()`, `sev_es_check_ghcb_fault()`, and `early_is_sevsnp_guest()`. Persistent data includes `boot_ghcb_page`, `.data` pointer `boot_ghcb`, `snp_vmpl`, `ghcb_version`, and `boot_svsm_caa_pa`. It directly includes `startup/sev-shared.c`.

Control flow: `sev_enable()` clears stale `cc_blob_address`, verifies CPUID leaf `0x8000001f`, probes for SNP CC blob via EFI config table or setup_data, copies the SNP CPUID table, configures SVSM CA when needed, reads `MSR_AMD64_SEV`, negotiates GHCB for SEV-ES, checks SNP hypervisor features and VMPL rules, validates blob/MSR consistency, and sets `sme_me_mask`. GHCB setup decrypts and zeroes a page, initializes instruction decode tables, and registers the GHCB GPA for SNP. Shutdown maps the GHCB encrypted and non-present before handing off. SNP page-state APIs build `psc_desc` requests and call the shared page-state transition path.

Dependencies and integration: integrates with EFI config table scanning, Linux boot protocol setup_data, GHCB MSR/page protocols, SVSM services, CPUID table validation, compressed page-table helpers, and decompressor identity-map creation. `sev_prep_identity_maps()` ensures the CC blob and SNP CPUID page remain accessible after switchover.

Risks and test signals: misdetecting SNP or unsupported SNP features risks undefined confidential-guest behavior, so unsupported feature masks terminate the guest. GHCB page cache/encryption transitions are security-sensitive. Test signals include successful boots across plain, SEV, SEV-ES, SNP VMPL0, SNP+SVSM/non-VMPL0, `cc_blob_address` propagation, unsupported feature termination with exit info, and page-state transitions for memory acceptance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/compressed/sev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/compressed/sev.h -->
# sources/distributed-fs/ceph-client/arch/x86/boot/compressed/sev.h

Purpose: declares the compressed-stage SEV/SNP helpers and provides no-op stubs when AMD memory encryption is disabled.

Important APIs and state: declares `snp_accept_memory()`, `sev_get_status()`, and `early_is_sevsnp_guest()`. Under `CONFIG_AMD_MEM_ENCRYPT`, inline helpers `sev_es_rd_ghcb_msr()` and `sev_es_wr_ghcb_msr()` wrap raw reads/writes to `MSR_AMD64_SEV_ES_GHCB`.

Control flow: no standalone control flow; it gates real SEV functionality behind the config symbol and returns inert values otherwise.

Dependencies and integration: included by compressed boot code that must compile regardless of SEV config. It depends on `<asm/shared/msr.h>` for raw MSR helpers and on SEV MSR definitions.

Risks and test signals: the stub behavior must preserve non-SEV boot behavior without accidental references to unavailable symbols. Test by building with and without `CONFIG_AMD_MEM_ENCRYPT`, and by confirming GHCB MSR wrappers are used only in early code paths where raw MSR access is valid.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/compressed/sev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/compressed/string.c -->
# sources/distributed-fs/ceph-client/arch/x86/boot/compressed/string.c

Purpose: supplies decompressor-safe memory primitives before the normal kernel runtime exists and avoids compiler-generated builtins that might use unsupported instructions.

Important APIs and state: defines `memset()`, `memmove()`, and `memcpy()`, with KASAN aliases for `__memset`, `__memmove`, and `__memcpy`. It includes the generic boot `string.c` for non-memory string/parse helpers and keeps a private optimized `____memcpy()` using `rep movsl` on 32-bit or `rep movsq` on 64-bit.

Control flow: `memcpy()` detects a destination-after-source overlap and delegates to backward-copying `memmove()` after warning. Non-overlap uses the optimized copy path. `memset()` is a simple byte loop to remain predictable in the decompressor environment.

Dependencies and integration: used throughout compressed boot, decompression, SEV/TDX setup, EFI parsing, and page-table setup. It depends on `error.h` for `warn()`.

Risks and test signals: a compiler optimization that bypasses these functions could introduce FPU/SIMD or runtime dependencies too early. The overlap check changes unsafe `memcpy()` into `memmove()`, which avoids corruption but signals a bug. Test by decompressor builds across GCC/Clang, KASAN compressed builds, overlapping-copy cases, and early boot under minimal CPU feature conditions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/compressed/string.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/compressed/tdcall.S -->
# sources/distributed-fs/ceph-client/arch/x86/boot/compressed/tdcall.S

Purpose: brings the common Intel TDX TDCALL assembly implementation into the compressed kernel.

Important APIs and state: no new symbols are defined directly here beyond those from `../../coco/tdx/tdcall.S`, which implements low-level TDCALL/TDVMCALL entry mechanics.

Control flow: purely include-based at assembly time.

Dependencies and integration: consumed by compressed TDX support in `tdx.c` and by shared TDX hypercall code. It allows early decompressor code to use the same TDX ABI glue as the normal kernel CoCo TDX implementation.

Risks and test signals: ABI mismatches in the included assembly affect early TDX guest boot and port-I/O hypercalls. Build with `CONFIG_INTEL_TDX_GUEST`, boot a TDX guest, and verify early console/port I/O paths do not execute forbidden raw I/O instructions after detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/compressed/tdcall.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/compressed/tdx-shared.c -->
# sources/distributed-fs/ceph-client/arch/x86/boot/compressed/tdx-shared.c

Purpose: includes shared TDX hypercall support into the compressed kernel.

Important APIs and state: the file itself only includes `error.h` and `../../coco/tdx/tdx-shared.c`; symbols such as `__tdx_hypercall()` are provided by the included shared implementation.

Control flow: include-only; runtime behavior belongs to the shared TDX implementation.

Dependencies and integration: links the decompressor TDX I/O overrides in `tdx.c` with common TDX module call helpers and failure handling.

Risks and test signals: failures in this glue surface as early TDX boot failures or inability to use TDVMCALL for I/O. Build and boot TDX guests with early serial output enabled and exercise `early_tdx_detect()` path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/compressed/tdx-shared.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/compressed/tdx.c -->
# sources/distributed-fs/ceph-client/arch/x86/boot/compressed/tdx.c

Purpose: detects Intel TDX in the compressed boot path and replaces raw port I/O callbacks with TDVMCALL-based I/O helpers.

Important APIs and state: exports `early_tdx_detect()` and `__tdx_hypercall_failed()`. It defines `tdx_io_in()`, `tdx_io_out()`, and byte/word wrappers used to populate `pio_ops`. State is external via `pio_ops` from real-mode/compressed I/O support.

Control flow: `early_tdx_detect()` issues CPUID leaf `TDX_CPUID_LEAF_ID` and compares the returned vendor signature with `TDX_IDENT`. On match, it sets `pio_ops.f_inb`, `f_outb`, and `f_outw` to TDX hypercall wrappers. The wrappers fill `struct tdx_module_args` for `EXIT_REASON_IO_INSTRUCTION`, with direction, port, width, and value encoded in registers, then call `__tdx_hypercall()`.

Dependencies and integration: depends on boot `cpuflags.h`, `io.h`, shared TDX definitions, and the common TDX hypercall assembly. It is called early enough that subsequent setup console/BIOS-style port I/O can be virtualized correctly in a TDX guest.

Risks and test signals: if detection runs late, raw I/O instructions may #VE or fail in TDX. `tdx_io_in()` returns `UINT_MAX` on hypercall failure, which consumers must tolerate. Test with TDX and non-TDX boots, early serial/console paths, and failure injection for TDVMCALL to ensure `error()` is reached for unrecoverable failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/compressed/tdx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/compressed/tdx.h -->
# sources/distributed-fs/ceph-client/arch/x86/boot/compressed/tdx.h

Purpose: provides the compressed boot declaration or stub for TDX early detection.

Important APIs and state: declares `early_tdx_detect()` when `CONFIG_INTEL_TDX_GUEST` is enabled; otherwise provides an empty inline.

Control flow: no runtime logic beyond config-gated dispatch.

Dependencies and integration: lets generic compressed boot code call `early_tdx_detect()` unconditionally without adding config ifdefs around every call site.

Risks and test signals: build coverage with `CONFIG_INTEL_TDX_GUEST=y/n` is the main signal. Runtime signal is that non-TDX builds produce no TDX references and TDX builds can override `pio_ops`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/compressed/tdx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/compressed/vmlinux.lds.S -->
# sources/distributed-fs/ceph-client/arch/x86/boot/compressed/vmlinux.lds.S

Purpose: linker script for the compressed kernel image. It defines entry points, layout, section ordering, alignment, page-table section placement, debug sections, and assertions that forbid runtime relocations/PLT/GOT surprises.

Important APIs and state: exports linker symbols such as `_head`, `_ehead`, `_text`, `_etext`, `_rodata`, `_erodata`, `_sbat`, `_esbat`, `_data`, `_edata`, `_bss`, `_ebss`, `_pgtable`, `_epgtable`, and `_end`. Entry is `startup_64` on x86-64 and `startup_32` on x86-32.

Control flow: build-time layout only. It places `.head.text` at address 0, compressed rodata, text/noinstr text, rodata, optional `.sbat`, page-aligned data, bss, optional x86-64 `.pgtable`, then aligns `_end` to a page. It discards dynamic and metadata sections and asserts `.got`, `.plt`, `.rel.dyn`, and `.rela.dyn` are empty.

Dependencies and integration: tightly coupled to compressed head assembly assumptions, EFI PE section metadata in `header.S`, SBAT inclusion, early BSS clearing, and page-table setup.

Risks and test signals: layout changes can break absolute assumptions in head code or EFI loaders. The assertions are important build-time tests for accidental compiler/linker features. Validate by building 32-bit/64-bit, EFI/SBAT variants, checking section addresses with `readelf`, and booting compressed images.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/compressed/vmlinux.lds.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/copy.S -->
# sources/distributed-fs/ceph-client/arch/x86/boot/copy.S

Purpose: provides 16-bit setup-code memory copy and fill routines plus segment-aware copies to/from `%fs`.

Important APIs and state: defines `memcpy`, `memset`, `copy_from_fs`, and `copy_to_fs` as 16-bit callable routines using `retl`. They operate on registers following the setup-code convention rather than normal C ABI details.

Control flow: `memcpy` copies dwords then bytes using `rep movsl/movsb`; `memset` expands a byte to a 32-bit pattern and stores dwords then bytes. `copy_from_fs` temporarily loads `%fs` into `%ds`; `copy_to_fs` temporarily loads `%fs` into `%es`, then delegates to `memcpy`.

Dependencies and integration: used by real-mode boot C code for BIOS data areas and video memory access through `set_fs()`, `rdfs*`, and screen save/restore logic.

Risks and test signals: segment register save/restore mistakes corrupt later BIOS calls or screen memory. Test by booting through video mode selection, EDD/BIOS probing, and screen restore paths that exercise `%fs` copies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/copy.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/cpu.c -->
# sources/distributed-fs/ceph-client/arch/x86/boot/cpu.c

Purpose: user-facing wrapper around CPU requirement checks in setup code. It reports a readable failure reason when the CPU family or required feature flags are missing.

Important APIs and state: exports `validate_cpu()`. Helpers `cpu_name()` and `show_cap_strs()` format the required CPU family and missing feature names from generated `x86_cap_strs`.

Control flow: calls `check_cpu()` to populate detected level, required level, and missing feature flags. It prints family mismatch, feature-list mismatch, or KNL erratum failure, returning `-1`; otherwise returns 0.

Dependencies and integration: called by `main()` before BIOS mode setup and protected-mode transition. Depends on `cpucheck.c`, generated `cpustr.h`, and early `printf()`/`puts()`.

Risks and test signals: missing generated cap strings fall back to numeric word:bit output, but incorrect masks can block valid CPUs or permit invalid ones. Test by builds with different `CONFIG_X86_MINIMUM_CPU_FAMILY` and required feature masks, plus QEMU CPU models missing specific flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/cpu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/cpucheck.c -->
# sources/distributed-fs/ceph-client/arch/x86/boot/cpucheck.c

Purpose: performs low-level early CPU capability validation for setup code without normal kernel services.

Important APIs and state: exports `check_cpu()` and `check_knl_erratum()`. Static data includes `err_flags[]`, required family `req_level`, and `req_flags[]` assembled from `REQUIRED_MASK*` macros. Vendor helpers compare raw CPUID vendor words.

Control flow: `check_cpu()` clears `cpu.flags`, assumes 386, probes AC flag for 486+, loads CPUID flags, computes missing flags, treats LM as level 64, and applies vendor-specific fixups: enabling AMD SSE/SSE2 through K7 HWCR, enabling VIA CX8, unmasking Transmeta flags, and optional `forcepae` for affected Pentium M models. It then checks the Xeon Phi KNL non-PAE 32-bit erratum and returns failure on insufficient level or missing flags.

Dependencies and integration: used by `cpu.c`, depends on boot `cpuflags.c`, command-line parsing, raw MSR access, and generated cpufeature masks.

Risks and test signals: raw MSR writes can be hazardous if vendor/model detection is wrong; `loaded_flags` behavior in `cpuflags.c` means repeated probes after attempted feature enabling need careful coordination. Test with QEMU CPU models for AMD, VIA/Centaur, Transmeta-like paths if available, Pentium M `forcepae`, and 32-bit KNL erratum guard.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/cpucheck.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/cpuflags.c -->
# sources/distributed-fs/ceph-client/arch/x86/boot/cpuflags.c

Purpose: gathers CPU feature flags in the minimal boot environment.

Important APIs and state: defines global `struct cpu_features cpu`, `u32 cpu_vendor[3]`, static `loaded_flags`, `cpuid_count()`, `get_cpuflags()`, and 32-bit `has_eflag()`. `has_fpu()` tests FPU availability by clearing CR0 EM/TS, running `fninit`, and checking status/control words.

Control flow: `get_cpuflags()` is idempotent. It records FPU, checks CPUID availability through EFLAGS.ID, reads vendor and basic leaf 1 flags/family/model, leaf 7 subleaf 0 ECX flags into word 16, and extended leaf `0x80000001` flags into words 6 and 1.

Dependencies and integration: supports `cpucheck.c`, TDX detection, and other setup code needing CPUID. Depends on bit operations and early raw assembly only.

Risks and test signals: because `loaded_flags` prevents repeated CPUID loading, feature-fixup code must update `cpu.flags` or deliberately re-probe around it. FPU probing mutates CR0 bits. Test on 32-bit and 64-bit builds, CPUs without CPUID, and feature-specific QEMU models.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/cpuflags.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/cpuflags.h -->
# sources/distributed-fs/ceph-client/arch/x86/boot/cpuflags.h

Purpose: declares the minimal CPU feature structure and CPUID helpers used by setup and compressed boot code.

Important APIs and state: `struct cpu_features` stores level, family, model, and `flags[NCAPINTS]`. Externs expose `cpu` and `cpu_vendor`. Declares `has_eflag()`, `get_cpuflags()`, `cpuid_count()`, and `has_cpuflag()`. On non-32-bit builds, `has_eflag()` is stubbed true.

Control flow: none; it is a contract header.

Dependencies and integration: included by CPU validation and TDX detection. It bridges setup code with asm cpufeature definitions without pulling in full kernel CPU infrastructure.

Risks and test signals: declaration mismatch with implementations or NCAPINTS changes can break early CPU validation. Compile-test with 32-bit and 64-bit configurations and required feature masks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/cpuflags.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/ctype.h -->
# sources/distributed-fs/ceph-client/arch/x86/boot/ctype.h

Purpose: supplies tiny boot-local character classification helpers.

Important APIs and state: inline `isdigit()` and `isxdigit()` only. No state.

Control flow: simple range checks for decimal and hexadecimal characters.

Dependencies and integration: used by early string parsing and printf field-width parsing where libc is unavailable.

Risks and test signals: only ASCII digits/hex letters are supported, which is correct for boot command-line parsing. Test through numeric command-line options and string conversion helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/ctype.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/early_serial_console.c -->
# sources/distributed-fs/ceph-client/arch/x86/boot/early_serial_console.c

Purpose: initializes early serial output for setup and compressed boot messages from `earlyprintk=` or `console=uart8250,io,...`.

Important APIs and state: exports `console_init()`. Helpers parse command-line options, probe an existing UART divisor, and program 8250-compatible UART registers. It writes global `early_serial_base` used by `tty.c`.

Control flow: `console_init()` first parses `earlyprintk`; if no serial base was established, it parses the last `console` option for `uart8250,io` or `uart,io`. `early_serial_init()` configures 8n1, disables interrupts/FIFO, asserts DTR/RTS, sets baud divisor, and stores the base port.

Dependencies and integration: depends on boot command-line parsing, `simple_strtoull()`, and port I/O callbacks, which TDX can override. `tty.c` mirrors output to this serial base.

Risks and test signals: malformed baud or port options fall back to defaults; `probe_baud()` can divide by zero if a UART reports a zero divisor. Test with `earlyprintk=serial,ttyS0,115200`, explicit hex ports, `console=uart8250,io,...`, and TDX port-I/O virtualization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/early_serial_console.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/edd.c -->
# sources/distributed-fs/ceph-client/arch/x86/boot/edd.c

Purpose: queries BIOS Enhanced Disk Drive information and optional MBR signatures for handoff in `boot_params`.

Important APIs and state: under `CONFIG_EDD` or `CONFIG_EDD_MODULE`, exports `query_edd()`. Helpers `get_edd_info()`, `read_mbr()`, and `read_mbr_sig()` use INT 13h. State is persisted in `boot_params.eddbuf`, `eddbuf_entries`, `edd_mbr_sig_buffer`, and `edd_mbr_sig_buf_entries`.

Control flow: command-line `edd=off/on/skipmbr/skip` controls probing. For BIOS drives `0x80` through the MBR signature max, it checks extensions, stores EDD params up to `EDDMAXNR`, and optionally reads the first sector to collect valid MBR signatures using heap space.

Dependencies and integration: called by `main()` when configured. Depends on BIOS calls, heap availability for MBR buffers, early strings, and Linux EDD structures.

Risks and test signals: buggy BIOSes can hang EDD probing, hence the user-facing `edd=off` hint. Heap shortage disables MBR signature reads. Test with EDD on/off/skipmbr, BIOS disks with and without valid MBR magic, and quiet vs non-quiet output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/edd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/genimage.sh -->
# sources/distributed-fs/ceph-client/arch/x86/boot/genimage.sh

Purpose: build helper for `make bzdisk`, floppy images, hard-disk images, and ISO images around an x86 bzImage plus optional initrds and command line.

Important APIs and state: shell entry arguments are disk format, output image, bzImage, mtools config, command line, and initrds. Functions include `verify`, `die`, `le`, `efiarch`, `filesizes`, `sharedirs`, `efidirs`, `findsyslinux`, `findovmf`, `do_mcopy`, `genbzdisk`, `genfdimage144`, `genfdimage288`, `genhdimage`, and `geniso`. State is temporary shell variables and generated image files.

Control flow: validates the kernel image, gathers readable initrds, detects EFI architecture from PE headers, finds syslinux/isolinux/OVMF assets, removes any previous output image, and dispatches by requested format. Disk-image paths use mtools/syslinux; ISO path builds a temporary isolinux tree and runs `genisoimage` plus optional `isohybrid`.

Dependencies and integration: invoked by arch/x86 boot Makefile targets. Requires bash, syslinux/isolinux, mtools, genisoimage, and sometimes OVMF/EDK2 shell. `mtools.conf.in` supplies drive mappings.

Risks and test signals: external tool availability and distro-specific asset paths are the main risks. The script intentionally sends `USR1` to its top shell on fatal errors. Test each image target, initrd option generation for syslinux/EFI, EFI arch detection, missing-tool failure messages, and cleanup of temporary ISO directory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/genimage.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/header.S -->
# sources/distributed-fs/ceph-client/arch/x86/boot/header.S

Purpose: defines the x86 boot sector/setup header, optional EFI PE headers, boot protocol fields, decompression size calculations, and real-mode setup entry that reaches C `main()`.

Important APIs and state: exports labels such as `sentinel`, `hdr`, `_start`, `realmode_swtch`, `kernel_version`, `start_of_setup`, and `die`. Header fields include load flags, command-line pointer, ramdisk fields, setup_data, preferred address, xloadflags, payload offset/length, init size, and handover offset. EFI builds emit DOS/PE/COFF optional headers and `.setup`, `.compat`, `.text`, optional `.sbat`, and `.data` section records.

Control flow: execution begins in 16-bit setup code, normalizes segments/stack, handles ancient loader stack quirks, far-returns to normalize `%cs`, verifies setup signature, clears BSS, calls C `main()`, and halts on corruption. Build-time macros compute safe in-place decompression offsets for supported compressors and choose `INIT_SIZE`.

Dependencies and integration: central to Linux x86 boot protocol compatibility and EFI stub entry. Depends on generated zoffset/voffset symbols, `boot.h`, kernel config flags, compressed linker symbols, and the C setup code.

Risks and test signals: changing offsets can break bootloaders that expect exact protocol field positions. PE metadata must match compressed linker layout. Test BIOS and EFI boots, mixed EFI, handover protocol, SBAT builds, legacy command-line loaders, and `tools/build` validation of bzImage headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/header.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/install.sh -->
# sources/distributed-fs/ceph-client/arch/x86/boot/install.sh

Purpose: legacy `make install` helper for copying an x86 kernel image and System.map into the install directory and invoking LILO when present.

Important APIs and state: shell arguments are kernel version, image path, map path, and install path. It rotates existing `vmlinuz` and `System.map` to `.old`, writes new files, and calls `/sbin/lilo` or `/etc/lilo/install`.

Control flow: `set -e` aborts on command failures. Existing files are moved, then image is copied via `cat` and map via `cp`; fallback is `sync` plus a warning if LILO is absent.

Dependencies and integration: invoked by kernel install target on systems using this script. Depends on shell utilities and optional LILO.

Risks and test signals: paths are unquoted, so install paths with spaces are unsafe. Rotation overwrites previous `.old` backups. Test with temporary install roots, missing LILO, and existing/new file replacement behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/install.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/io.h -->
# sources/distributed-fs/ceph-client/arch/x86/boot/io.h

Purpose: defines boot-time port I/O indirection so normal x86 I/O instructions can be replaced in TDX guests.

Important APIs and state: `struct port_io_ops` holds `f_inb`, `f_outb`, and `f_outw`; external `pio_ops` stores active callbacks. `init_default_io_ops()` installs `__inb`, `__outb`, and `__outw`. Macros redefine `inb`, `outb`, and `outw` to call through `pio_ops`.

Control flow: callers initialize defaults early, then TDX detection may override callbacks.

Dependencies and integration: included by setup and compressed code that uses port I/O, including serial, PIC masking, VGA, and TDX paths.

Risks and test signals: code using `inw/inl/outl` is not redirected here. Missing `init_default_io_ops()` leaves null callbacks. Test non-TDX boot for default callbacks and TDX boot for hypercall callbacks before first sensitive I/O.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/io.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/main.c -->
# sources/distributed-fs/ceph-client/arch/x86/boot/main.c

Purpose: orchestrates real-mode setup before jumping to protected mode.

Important APIs and state: defines aligned global `struct boot_params boot_params`, `struct port_io_ops pio_ops`, heap pointers `HEAP` and `heap_end`, and entry `main()`. Local helpers copy boot params, initialize keyboard, query Intel SpeedStep IST, tell BIOS intended long mode, and initialize heap bounds.

Control flow: `main()` initializes default I/O ops, copies header fields into zeropage, initializes console, optionally prints debug, bounds heap, validates CPU, notifies BIOS of mode, detects memory, initializes keyboard, queries IST/APM/EDD, selects video, and calls `go_to_protected_mode()`.

Dependencies and integration: entered from `header.S`. It feeds `boot_params` to later protected-mode/compressed kernel stages. Depends on BIOS interrupts, command-line parsing, CPU/memory/video modules, and `pm.c`.

Risks and test signals: order matters: console before diagnostics, CPU validation before mode switch, memory/video before boot_params handoff. Test legacy and modern bootloaders, old command-line protocol conversion, heap-limited boots, debug output, and all configured optional probe paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/memory.c -->
# sources/distributed-fs/ceph-client/arch/x86/boot/memory.c

Purpose: detects system memory through BIOS interfaces and stores results in boot parameters.

Important APIs and state: exports `detect_memory()`. Helpers query INT 15h E820, E801, and AH=88h. State is written to `boot_params.e820_table`, `e820_entries`, `alt_mem_k`, and `screen_info.ext_mem_k`.

Control flow: E820 loops with a static zeroed buffer to handle BIOSes that partially update entries, copies valid SMAP entries until continuation ends or table fills, and zeroes count on signature loss. E801 and 88h provide older fallback size fields.

Dependencies and integration: called by `main()` before protected mode. Later kernel memory initialization uses these boot protocol fields.

Risks and test signals: firmware bugs can produce partial or bogus maps; E820 signature loss intentionally invalidates the map. Test with QEMU e820 variants, table-full conditions, non-SMAP failure, and legacy memory-size fallback behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/memory.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/mkcpustr.c -->
# sources/distributed-fs/ceph-client/arch/x86/boot/mkcpustr.c

Purpose: host-side generator that emits compact CPU feature-name strings for setup-code diagnostics.

Important APIs and state: standalone `main()` includes kernel cpufeature tables and prints C source defining `x86_cap_strs[]`. It only emits strings for features present in `REQUIRED_MASK*`, with each string prefixed by capability word and bit bytes.

Control flow: nested loops over `NCAPINTS` and 32 bits lookup `x86_cap_flags`, conditionally print preprocessor guards, and ensure the last entry is unconditional so the generated string is terminated.

Dependencies and integration: built and run during arch/x86 boot build to generate `cpustr.h`, included by `cpu.c`.

Risks and test signals: generated encoding must match `show_cap_strs()` parser. Test by regenerating after cpufeature table changes and by forcing missing required flags to verify readable output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/mkcpustr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/mtools.conf.in -->
# sources/distributed-fs/ceph-client/arch/x86/boot/mtools.conf.in

Purpose: template mtools configuration for x86 boot image generation.

Important APIs and state: defines drives `a:`, `v:`, `w:`, `h:`, and `p:` mapping to floppy device, 1.44 MB image, 2.88 MB image, and hard-disk image/partition using `@OBJ@` substitution.

Control flow: none; consumed by mtools commands run from `genimage.sh`.

Dependencies and integration: generated into a concrete config file by the build system and exported as `MTOOLSRC`.

Risks and test signals: wrong object directory substitution or geometry breaks image creation. Test `make fdimage144`, `fdimage288`, and `hdimage` targets using the generated config.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/mtools.conf.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/pm.c -->
# sources/distributed-fs/ceph-client/arch/x86/boot/pm.c

Purpose: prepares the CPU and interrupt hardware for transition from real mode to protected mode.

Important APIs and state: exports `go_to_protected_mode()`. Local helpers handle optional real-mode switch hook, interrupt masking, FPU IGNNE reset, GDT setup, and IDT setup. Static GDT contains boot CS, DS, and TSS descriptors.

Control flow: calls loader-provided `realmode_swtch` or disables interrupts/NMI, enables A20, resets coprocessor, masks PIC interrupts, loads a null IDT and boot GDT, then calls `protected_mode_jump()` with `code32_start` and the physical boot_params address.

Dependencies and integration: called at the end of `main()`. Depends on BIOS/port I/O, A20 helper, boot protocol fields, and `pmjump.S`.

Risks and test signals: failures in A20 or descriptor setup prevent boot. The static GDT pointer workaround supports Xen HVM quirks. Test legacy BIOS, Xen HVM, A20 failure injection, and bootloader real-mode switch hook behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/pm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/pmjump.S -->
# sources/distributed-fs/ceph-client/arch/x86/boot/pmjump.S

Purpose: performs the final architectural switch from 16-bit real mode into 32-bit protected mode and jumps to the kernel entry point.

Important APIs and state: defines `protected_mode_jump(u32 entrypoint, u32 bootparams)`. No persistent data.

Control flow: saves boot_params pointer in `%esi`, computes real-mode segment base, sets PE in CR0, far-jumps to 32-bit code segment, loads flat data segments, adjusts stack to linear address, loads TR and LDTR, clears extension registers, and jumps to the entrypoint in `%eax`.

Dependencies and integration: called by `pm.c` after GDT/IDT setup. Uses boot segment selectors from asm headers and assumes the GDT entries loaded by `setup_gdt()`.

Risks and test signals: incorrect segment base or selector values hang immediately. Test by BIOS booting bzImage, debug tracing around protected-mode entry, and QEMU CPU models including old 386/486 serialization behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/pmjump.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/printf.c -->
# sources/distributed-fs/ceph-client/arch/x86/boot/printf.c

Purpose: provides small boot-time formatting functions for diagnostics without full libc or kernel printf.

Important APIs and state: defines `vsprintf()`, `sprintf()`, and `printf()`. Helpers `skip_atoi()` and `number()` implement integer formatting. `printf()` uses a fixed 1024-byte stack buffer and writes through `puts()`.

Control flow: parser supports flags, width, precision, `h/l/L` qualifiers, `%c`, `%s`, `%p`, `%n`, `%%`, and integer formats in bases 8/10/16. It explicitly lacks full 64-bit formatting support beyond `unsigned long`.

Dependencies and integration: used by CPU, EDD, video, and diagnostic paths. Depends on boot `ctype.h`, `strnlen()`, and `tty.c`.

Risks and test signals: no bounds checking on the output buffer means long formatted output can overflow. Test normal boot diagnostics, missing CPU features, video menu output, and format cases used by setup code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/printf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/regs.c -->
# sources/distributed-fs/ceph-client/arch/x86/boot/regs.c

Purpose: initializes BIOS register blocks before interrupt calls.

Important APIs and state: exports `initregs(struct biosregs *reg)`.

Control flow: zeroes the register block, sets carry flag in `eflags` as a defensive default, and initializes `ds`, `es`, `fs`, and `gs` from current segment helper functions.

Dependencies and integration: used by nearly every BIOS-interrupt caller in setup code, including memory, keyboard, video, EDD, and tty.

Risks and test signals: default CF helps detect BIOS helper paths that fail to clear status. Segment initialization must match the setup environment. Test by exercising BIOS calls and verifying callers handle CF correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/regs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/startup/Makefile -->
# sources/distributed-fs/ceph-client/arch/x86/boot/startup/Makefile

Purpose: builds the position-independent x86-64 startup support objects used before normal kernel relocation and instrumentation are available.

Important APIs and state: configures special CFLAGS/AFLAGS, disables tracing/LTO/sanitizers/coverage, selects objects (`gdt_idt.o`, `map_kernel.o`, `sme.o`, `sev-startup.o`, `la57toggle.o`, `efi-mixed.o`), and transforms startup object symbols with `objcopy --prefix-symbols=__pi_`. It invokes objtool with `--noabs` on PI objects.

Control flow: make rules compile regular objects, prefix them into `.pi.o`, then replace `obj-y` with PI outputs. Library objects are marked non-standard for objtool.

Dependencies and integration: works with linker-provided aliases in `exports.h` so runtime code can call selected PI implementations. It is critical for early identity-mapped execution.

Risks and test signals: missing flags can introduce instrumentation, stack protector, jump tables, absolute relocations, or LTO output that is unsafe in early boot. Test with objtool no-absolute-relocation checks, sanitizer-enabled configs, EFI mixed-mode configs, and AMD memory encryption configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/startup/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/startup/efi-mixed.S -->
# sources/distributed-fs/ceph-client/arch/x86/boot/startup/efi-mixed.S

Purpose: supports invoking 32-bit EFI services and entering a 64-bit kernel from 32-bit EFI firmware in mixed-mode EFI boots.

Important APIs and state: defines `efi32_stub_entry`, local `efi_enter32`, `__efi64_thunk`, `efi32_enable_long_mode`, `efi32_startup`, `efi32_pe_entry`, optional `efi64_stub_entry`, data `efi32_call`, `efi_is64`, and a 6-page page-table buffer `pte`.

Control flow: 32-bit EFI entry clears BSS, extracts `boot_params`, and jumps to startup. `efi32_startup` saves/copies firmware GDT, appends a 64-bit code descriptor, builds identity page tables, enables PAE/LME/paging, records mixed mode, prepares a far-call gate back to 32-bit firmware, and long-jumps to `efi_stub_entry`. `__efi64_thunk` far-calls `efi_enter32`, which converts x86-64 ABI arguments to 32-bit stack arguments, disables paging/long mode, calls firmware, then re-enables long mode.

Dependencies and integration: tied to EFI stub, PE header entries in `header.S`, x86 GDT/MSR/page-table definitions, and identity mappings before virtual-address transition.

Risks and test signals: mode-switching and firmware GDT restoration are fragile; argument truncation is intentional because early identity mappings keep addresses under 4 GiB. Test 64-bit kernel on 32-bit EFI firmware, EFI handover protocol, EFI boot service calls through thunking, and unsupported CPU long-mode return path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/startup/efi-mixed.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/startup/exports.h -->
# sources/distributed-fs/ceph-client/arch/x86/boot/startup/exports.h

Purpose: linker alias header exposing selected position-independent startup symbols under their runtime names.

Important APIs and state: `PROVIDE()` aliases include `early_set_pages_state`, `early_snp_set_memory_private`, `early_snp_set_memory_shared`, `get_hv_features`, `sev_es_terminate`, `snp_cpuid`, `snp_cpuid_get_table`, `svsm_issue_call`, and `svsm_process_result_codes` to their `__pi_` prefixed implementations.

Control flow: build/link-time only.

Dependencies and integration: matches the `objcopy --prefix-symbols=__pi_` rule in startup `Makefile`. Runtime SEV code can call these functions while the actual implementation came from PI startup objects.

Risks and test signals: aliases must stay synchronized with startup implementation symbol names and consumers. Link failures catch many mismatches; SEV/SNP boot tests catch semantic drift.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/startup/exports.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/startup/gdt_idt.c -->
# sources/distributed-fs/ceph-client/arch/x86/boot/startup/gdt_idt.c

Purpose: loads early GDT and IDT state for 64-bit startup before the normal kernel IDT is available.

Important APIs and state: defines page-aligned `bringup_idt_table`, `startup_64_load_idt(void *vc_handler)`, and `startup_64_setup_gdt_idt()`.

Control flow: `startup_64_setup_gdt_idt()` obtains a RIP-relative pointer to `gdt_page`, loads the GDT, reloads data segments, selects `vc_no_ghcb` as a #VC handler when AMD memory encryption is enabled, and calls `startup_64_load_idt()`. The IDT loader optionally initializes a #VC descriptor in the bringup table and loads it.

Dependencies and integration: called from `head_64.S` during boot CPU and secondary CPU bringup. Depends on descriptor helpers, RIP-relative access, and SEV early VC handler.

Risks and test signals: using runtime `idt_table` too early would run instrumented code or require unavailable CPU state, so this local table is essential. Test normal, SEV-ES/SNP, and secondary CPU startup paths with early #VC delivery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/startup/gdt_idt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/startup/la57toggle.S -->
# sources/distributed-fs/ceph-client/arch/x86/boot/startup/la57toggle.S

Purpose: template trampoline code copied below 4 GiB to toggle CR4.LA57 while temporarily leaving long mode.

Important APIs and state: exports `trampoline_32bit_src` and data `trampoline_ljmp_imm_offset`. The code size is bounded by `.org trampoline_32bit_src + TRAMPOLINE_32BIT_CODE_SIZE`.

Control flow: 64-bit entry saves callee-saved registers and upper RSP bits, far-returns to 32-bit compatibility code, disables paging, loads CR3 from `%edi`, ensures EFER.LME is set, toggles CR4.LA57, re-enables paging, and far-jumps back to the relocated 64-bit return label. On return it reconstructs RSP and restores registers.

Dependencies and integration: copied and patched by compressed `pgtable_64.c`. It uses kernel segment selectors, MSR_EFER, CR0/CR4 flags, and the low-memory temporary page table.

Risks and test signals: stack address truncation, incorrect far-jump relocation, or code-size overflow will break LA57 switching. Test 4-to-5 and 5-to-4 transitions, high stack addresses, TDX guests where unnecessary EFER writes are avoided, and build-time code-size assertion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/startup/la57toggle.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/startup/map_kernel.c -->
# sources/distributed-fs/ceph-client/arch/x86/boot/startup/map_kernel.c

Purpose: performs early x86-64 kernel page-table fixups, identity mapping, LA57 propagation, and SME post-processing while running from early identity mappings.

Important APIs and state: exports `__startup_64(unsigned long p2v_offset, struct boot_params *bp)`. Helpers include `check_la57_support()` and `sme_postprocess_startup()`. It manipulates global early page tables, `phys_base`, `next_early_pgt`, `__pgtable_l5_enabled`, `pgdir_shift`, and `ptrs_per_p4d`.

Control flow: detects active LA57 via CR4, validates physical address and 2 MiB alignment, computes load delta and virtual text range, fixes top-level/kernel/fixmap page-table entries, builds identity mappings around the current physical location using early dynamic page tables, fixes or invalidates `level2_kernel_pgt` entries around the actual image, calls `sme_encrypt_kernel()`, changes `.bss..decrypted` mappings to decrypted/shared as needed, and returns the encryption mask for CR3 setup.

Dependencies and integration: called by `head_64.S` before virtual-address execution. Depends on RIP-relative addressing, early page-table globals, SME/SNP helpers, and linker symbols `_text`, `_end`, `__start_bss_decrypted`, and `__end_bss_decrypted`.

Risks and test signals: invalid mappings can allow speculative access to reserved memory or crash before diagnostics. Test relocatable kernels, 4-level/5-level paging, SME active/non-active, SNP page-state transitions for decrypted BSS, and kernels loaded at non-preferred but 2 MiB-aligned addresses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/startup/map_kernel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/startup/sev-shared.c -->
# sources/distributed-fs/ceph-client/arch/x86/boot/startup/sev-shared.c

Purpose: shared SEV/SNP/SVSM early-boot implementation included into both compressed boot and startup/runtime PI code.

Important APIs and state: provides `sev_es_terminate()`, `get_hv_features()`, `svsm_process_result_codes()`, `svsm_issue_call()`, `svsm_perform_msr_protocol()`, `snp_cpuid_get_table()`, `snp_cpuid()`, `do_vc_no_ghcb()`, `find_cc_blob_setup_data()`, `setup_cpuid_table()`, `svsm_setup_ca()`, and page-state internals including `__page_state_change()` and `pvalidate_4k_page()`. Static persistent state includes `cpuid_table_copy`, CPUID range maxima, and `sev_snp_needs_sfw`.

Control flow: termination writes GHCB MSR termination requests and halts. HV features and CPUID can use the GHCB MSR protocol. SNP CPUID handling validates firmware table entries, computes XSAVE sizes, post-processes dynamic APIC/OSXSAVE/PKE/topology values via hypervisor callbacks, and supports sparse zero leaves. The no-GHCB #VC handler only accepts CPUID, fills registers, validates SEV leaves, advances RIP, or terminates. Page-state changes pvalidate before/after GHCB PSC requests depending on shared/private direction, with SVSM-mediated PVALIDATE for non-VMPL0 guests.

Dependencies and integration: included directly into `compressed/sev.c` and startup `sev-startup.c`. Depends on GHCB MSR operations supplied by the includer, SNP CC blob structures, setup_data lists, SVSM calling area structures, CPUID helpers, and raw early interrupt/MSR primitives.

Risks and test signals: this is security-critical. CPUID table validation prevents hypervisor spoofing; page-state ordering must match SNP RMP semantics; SVSM CA setup must correctly identify VMPL0 vs non-VMPL0 via RMPADJUST. Test SEV-ES CPUID #VC before GHCB, SNP sparse CPUID tables, unsupported CPUID table entries, VMPL0 and SVSM guests, PSC failure termination, and cache-eviction mitigation when `sev_snp_needs_sfw` is set.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/startup/sev-shared.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/startup/sev-startup.c -->
# sources/distributed-fs/ceph-client/arch/x86/boot/startup/sev-startup.c

Purpose: startup-side SEV/SNP helpers for early page-state changes and SNP initialization after or without the compressed boot stage.

Important APIs and state: exports `early_set_pages_state()`, `early_snp_set_memory_private()`, `early_snp_set_memory_shared()`, and `snp_init()`. It includes `sev-shared.c` and uses `boot_svsm_ca_page`, `boot_svsm_caa_pa`, `sev_status`, and `sev_secrets_pa`.

Control flow: memory-private/shared functions build `psc_desc` values and call `early_set_pages_state()` page by page only when SNP is enabled. `snp_init()` finds the CC blob via `boot_params.cc_blob_address` or setup_data, caches the secrets page PA, copies the CPUID table, runs SVSM setup/remap for non-VMPL0 guests, caches the blob address back into boot params, and returns whether SNP setup was performed.

Dependencies and integration: called by `sme_enable()` and early mapping code while identity mapped. Depends on shared SEV functions, boot params, CC blob/secrets page, and SVSM MSR protocol.

Risks and test signals: blob/MSR mismatch terminates later in `sme_enable()`. Non-VMPL0 remap must occur while old and new CA addresses are still usable. Test direct firmware/PVH boot with setup_data CC blob, compressed boot handoff via `cc_blob_address`, SNP secrets-page presence, and shared/private page transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/startup/sev-startup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/startup/sme.c -->
# sources/distributed-fs/ceph-client/arch/x86/boot/startup/sme.c

Purpose: detects and enables AMD memory encryption state during startup and performs in-place kernel/initrd encryption for SME.

Important APIs and state: exports `sme_encrypt_kernel(struct boot_params *bp)`, `sme_enable(struct boot_params *bp)`, and local PTI stub `__pti_set_user_pgtbl()` when needed. Internal state includes `sme_workarea` in `.init.scratch` and `struct sme_populate_pgd_data` for temporary page-table construction.

Control flow: `sme_enable()` initializes SNP, verifies AMD SME/SEV CPUID leaf, reads SEV MSR, checks CC blob/SNP consistency, filters SME in hypervisors, checks SYSCFG memory-encryption enablement, and sets `sme_me_mask`, `physical_mask`, `cc_vendor`, and `cc_mask`. `sme_encrypt_kernel()` returns unless SME is active and SEV is not. It computes kernel/initrd/workarea ranges, calculates page-table memory, maps workarea decrypted in current tables, builds a fresh PGD with encrypted identity mappings and decrypted write-protected alternate mappings for kernel/initrd, maps workarea in both views, calls `sme_encrypt_execute()`, removes decrypted mappings, and flushes TLBs.

Dependencies and integration: used by `map_kernel.c` before final virtual mapping. Depends on early page-table helpers, boot params/initrd fields, SNP setup, AMD MSRs, encryption execution assembly, and CoCo core mask state.

Risks and test signals: in-place encryption must not overlap boot params or initrd, and temporary mappings must be non-cacheable/write-protected where required. Test SME bare metal with and without initrd, SEV guests bypassing SME encryption, SNP blob consistency failure, hypervisor-bit SME suppression, and post-encryption execution with decrypted mappings removed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/startup/sme.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/string.c -->
# sources/distributed-fs/ceph-client/arch/x86/boot/string.c

Purpose: implements small string, memory, and integer parsing helpers for x86 boot/setup code.

Important APIs and state: defines `memcmp()`, `bcmp()`, `strcmp()`, `strncmp()`, `strnlen()`, `simple_strtoull()`, `simple_strtol()`, `strlen()`, `strstr()`, `strchr()`, `kstrtoull()`, and `boot_kstrtoul()`. Helpers implement radix guessing, 64-bit division by 32-bit divisor, overflow-aware integer parsing, and simple ASCII lowercase.

Control flow: simple string routines iterate byte-wise or use `repe cmpsb`. `simple_strtoull()` parses permissively and returns end pointer. `kstrtoull()` accepts optional plus, auto-detects base 0, detects overflow with `KSTRTOX_OVERFLOW`, permits one trailing newline, and returns `-EINVAL`/`-ERANGE` on errors.

Dependencies and integration: used by command-line parsers, early serial, video options, and compressed string support. It undefines compiler macros for memory primitives so real symbols exist, then `string.h` redefines default calls to builtins where safe.

Risks and test signals: `memcmp()` returns only nonzero/zero rather than ordered difference, which is acceptable for current uses but not a full libc semantic. Test numeric parsing boundaries, hex/octal autodetect, overflow, command-line option parsing, and Clang lowering of memcmp to bcmp.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/string.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/string.h -->
# sources/distributed-fs/ceph-client/arch/x86/boot/string.h

Purpose: declares boot-local string/memory helpers and controls builtin use for setup code.

Important APIs and state: declares memory functions, comparison/string functions, simple numeric conversion, and checked conversion functions. It undefines `memcpy`, `memset`, and `memcmp`, then maps them to compiler builtins by default for callers.

Control flow: none; compile-time macro behavior only.

Dependencies and integration: included throughout x86 boot code. `compressed/string.c` deliberately provides custom memory implementations for the decompressor environment.

Risks and test signals: builtin mapping must not be used in contexts where compiler-generated code is unsafe. Build and boot with GCC/Clang, KASAN compressed aliases, and calls requiring addressable memory function symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/string.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/tty.c -->
# sources/distributed-fs/ceph-client/arch/x86/boot/tty.c

Purpose: provides early text input/output via BIOS console and optional serial mirroring.

Important APIs and state: defines global `early_serial_base`; exports `putchar()`, `puts()`, `getchar()`, `kbd_flush()`, and `getchar_timeout()`. Local helpers write serial, write BIOS teletype, read CMOS seconds, and test keyboard pending.

Control flow: `putchar()` converts newline to CRLF, writes BIOS INT 10h teletype, and mirrors to serial if initialized. Keyboard timeout polls INT 16h and BIOS time for about 30 seconds.

Dependencies and integration: used for all setup diagnostics, video menu interaction, CPU/EDD messages, and early serial output. Depends on BIOS INT 10h/16h/1Ah and port I/O indirection.

Risks and test signals: BIOS calls are unavailable after protected mode, so use is confined to setup/inittext. Serial transmit waits with a bounded timeout. Test video menu input, timeout behavior, CRLF output, and serial mirroring with `earlyprintk`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/tty.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/version.c -->
# sources/distributed-fs/ceph-client/arch/x86/boot/version.c

Purpose: embeds the kernel version string into the setup image.

Important APIs and state: defines `const char kernel_version[]` from generated `UTS_RELEASE`, `LINUX_COMPILE_BY`, `LINUX_COMPILE_HOST`, and `UTS_VERSION`.

Control flow: no runtime logic.

Dependencies and integration: `header.S` references `kernel_version` in the boot protocol header. Generated version headers are produced by the kernel build.

Risks and test signals: stale generated headers or layout changes can expose wrong version metadata to bootloaders/tools. Test by inspecting bzImage setup header version string after a build.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/version.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/vesa.h -->
# sources/distributed-fs/ceph-client/arch/x86/boot/vesa.h

Purpose: defines packed VESA BIOS Extension structures used by boot video probing.

Important APIs and state: declares `far_ptr`, `struct vesa_general_info`, `VESA_MAGIC`, and `struct vesa_mode_info`.

Control flow: no runtime logic; structure layout must match VBE BIOS ABI.

Dependencies and integration: used by `video-vesa.c` to call VBE functions, enumerate modes, store framebuffer geometry, and retrieve EDID.

Risks and test signals: packing or field-size errors corrupt BIOS data interpretation. Test VESA text and linear-framebuffer mode detection across BIOS/firmware implementations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/vesa.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/video-bios.c -->
# sources/distributed-fs/ceph-client/arch/x86/boot/video-bios.c

Purpose: registers and probes conventional BIOS text modes as a video backend.

Important APIs and state: defines a `__videocard video_bios` with `bios_probe()` and `bios_set_mode()`. Probe allocates mode descriptors on the boot heap and marks this backend `unsafe`, so it only scans after explicit user request.

Control flow: `bios_probe()` iterates BIOS modes `0x14..0x7f`, skips already-defined modes, sets each mode, verifies text-mode characteristics through VGA registers, records geometry from BIOS data area, then restores the saved mode. `set_bios_mode()` sets INT 10h mode, verifies current mode, and attempts revert if setting failed to a different mode.

Dependencies and integration: used by `probe_cards()`/`set_mode()` in video selection. Depends on VGA adapter detection, heap allocation, BIOS INT 10h, and indexed VGA register access.

Risks and test signals: probing is unsafe because real BIOS mode switches can blank or wedge displays; it is gated behind the menu scan path. Test manual `scan`, successful restore, duplicate mode filtering, and fallback/revert on failed mode set.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/video-bios.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/video-mode.c -->
# sources/distributed-fs/ceph-client/arch/x86/boot/video-mode.c

Purpose: shared video-mode selection engine used by setup code and ACPI wakeup code.

Important APIs and state: exports globals `adapter`, `force_x`, `force_y`, `do_restore`, and `graphic_mode`; functions `probe_cards()`, `mode_defined()`, and `set_mode()`.

Control flow: `probe_cards()` runs each registered `__videocard` probe once per safe/unsafe class. `raw_set_mode()` resolves a requested mode by menu index, exact mode id, resolution encoding, or exceptional unprobed range and calls the owning backend. `set_mode()` handles aliases (`NORMAL_VGA`, `EXTENDED_VGA`, current mode), optionally recalculates VGA vertical timing, and stores the canonical mode in boot params.

Dependencies and integration: central dispatcher for `video.c`, `video-vga.c`, `video-vesa.c`, and `video-bios.c`. Relies on linker-collected `.videocards` records.

Risks and test signals: mode-number compatibility can change if visible mode ordering changes, hence exact IDs are safer than menu indexes. Test aliases, resolution selections, VESA/BIOs exceptional modes, `VIDEO_RECALC`, and wakeup build path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/video-mode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/video-vesa.c -->
# sources/distributed-fs/ceph-client/arch/x86/boot/video-vesa.c

Purpose: implements VESA BIOS Extension text and optional graphics mode probing/setting for early boot.

Important APIs and state: defines static VBE info buffers `vginfo` and `vminfo`, a `__videocard video_vesa`, and `vesa_store_edid()` when not in wakeup. Helpers store graphics framebuffer parameters, DAC size, and VESA protected-mode info in `boot_params.screen_info`.

Control flow: `vesa_probe()` calls VBE `0x4f00`, validates signature/version, walks the BIOS mode list, queries mode info with `0x4f01`, and records supported text modes or configured linear-framebuffer graphics modes. `vesa_set_mode()` validates the target, sets mode with `0x4f02` and linear framebuffer bit when needed, updates text geometry or graphics framebuffer state. EDID probing uses VBE DDC `0x4f15`.

Dependencies and integration: participates in video card registry and feeds boot protocol `screen_info` for later console/framebuffer setup. Depends on VESA ABI structures, BIOS INT 10h, heap allocation, and config options `CONFIG_BOOT_VESA_SUPPORT` and `CONFIG_FIRMWARE_EDID`.

Risks and test signals: BIOS VBE implementations vary widely; framebuffer metadata must match actual mode or the kernel console will be wrong. Test VBE 1.2+ text modes, VBE 2.0 EDID, graphics LFB modes, DAC size handling, and builds without framebuffer support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/video-vesa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/video-vga.c -->
# sources/distributed-fs/ceph-client/arch/x86/boot/video-vga.c

Purpose: provides baseline CGA/EGA/VGA text mode detection and mode setting.

Important APIs and state: defines static mode tables for VGA, EGA, and CGA; exports `vga_crtc()`; registers `__videocard video_vga`. It updates global adapter type and boot screen flags.

Control flow: `vga_probe()` uses BIOS INT 10h EGA/VGA checks and display combination code to classify adapter, stores original EGA BX in boot params, and selects the appropriate mode list. Mode-setting resets to basic text mode, sets font/scans for requested 80-column text geometry, updates `force_x/force_y`, and uses CRTC register helpers for 480-scanline modes.

Dependencies and integration: must be listed first in the video Makefile because other video backends depend on adapter and CRTC information. Uses BIOS INT 10h and VGA indexed I/O ports.

Risks and test signals: direct CRTC programming is hardware-sensitive. Test CGA/EGA/VGA classification, 80x25/43/50/60 modes, cursor/font sizes, and that later VESA/BIOS probes see initialized adapter state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/video-vga.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/video.c -->
# sources/distributed-fs/ceph-client/arch/x86/boot/video.c

Purpose: top-level setup video selection, menu interaction, and screen-info capture.

Important APIs and state: exports `set_video()`. Internal state includes `video_segment` and heap-backed `saved_screen` data. Helpers store cursor/current mode/mode params, display interactive mode menus, save/restore text screen contents, and parse user mode entry.

Control flow: `set_video()` resets heap, stores current mode parameters, saves text screen, probes safe cards, resolves `hdr.vid_mode` through current/default/menu loop, retries undefined modes by asking user, stores canonical mode, saves EDID, refreshes mode params, and restores screen when requested. Menu flow waits for Enter/Space/timeout, supports `scan` to run unsafe probes, and accepts hex-like mode input.

Dependencies and integration: called by `main()` before protected mode. Writes `boot_params.screen_info` and `hdr.vid_mode` consumed by the kernel. Integrates all `__videocard` backends and real-mode I/O helpers.

Risks and test signals: heap space limits screen save and probed mode lists. User-visible menu path must work with BIOS keyboard/console and serial mirroring. Test default/current mode, `vga=ask`, `scan`, graphics mode no-restore behavior, screen restore, and geometry overrides from `force_x/force_y`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/video.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/video.h -->
# sources/distributed-fs/ceph-client/arch/x86/boot/video.h

Purpose: declares the real-mode video probing contract, mode-number namespace, and shared video state.

Important APIs and state: defines mode ranges for BIOS, VESA, Video7, special modes, resolution modes, and `VIDEO_RECALC`; structs `mode_info` and `card_info`; `__videocard` linker-section registration; externs for `video_cards`, `adapter`, `force_x`, `force_y`, `do_restore`, and `graphic_mode`; helpers for VGA indexed registers and `vga_crtc()`.

Control flow: no standalone runtime, but macros and structs define how video backends are discovered and invoked.

Dependencies and integration: included by all boot video files and by wakeup-shared mode code.

Risks and test signals: mode namespace collisions or struct layout changes break backend dispatch. Build and boot test all video backends and menu display.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/boot/video.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/coco/Makefile -->
# sources/distributed-fs/ceph-client/arch/x86/coco/Makefile

Purpose: builds common x86 confidential-computing support and conditionally includes TDX and SEV subdirectories.

Important APIs and state: removes `-pg` from `core.o`, disables KASAN for `core.o`, adds `-fno-stack-protector`, always builds `core.o`, and conditionally descends into `tdx/` and `sev/`.

Control flow: make-time only.

Dependencies and integration: controls instrumentation suitability for early/noinstr CoCo capability code and selects vendor-specific subtrees by config.

Risks and test signals: instrumentation in CoCo core could violate noinstr/early constraints. Test with profiling/sanitizer configs and both `CONFIG_INTEL_TDX_GUEST` and `CONFIG_AMD_MEM_ENCRYPT` combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/coco/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/coco/core.c -->
# sources/distributed-fs/ceph-client/arch/x86/coco/core.c

Purpose: centralizes x86 confidential-computing vendor state, platform attribute queries, page-table encryption-bit transformations, attribute flags, and early RNG seeding for encrypted guests.

Important APIs and state: defines `cc_vendor`, `cc_mask`, static `cc_flags`, and exports `cc_platform_has()` and `cc_mkdec()`. Also provides `cc_mkenc()`, `cc_platform_clear()`, `cc_platform_set()`, and `cc_random_init()`. PIC aliases expose `cc_vendor` and `cc_mask` to position-independent startup code.

Control flow: `cc_platform_has()` dispatches to AMD or Intel implementations. Intel reports memory encryption and string-I/O unroll needs. AMD handles vTOM separately, SME host encryption, SEV guest memory/state encryption, string-I/O unroll without SEV-ES, SNP, secure TSC, host SNP flag, and secure AVIC. `cc_mkenc()`/`cc_mkdec()` set or clear `cc_mask` according to AMD C-bit, AMD vTOM, or Intel semantics. `cc_random_init()` seeds kernel randomness with RDRAND for encrypted guests and panics if no random longs are available.

Dependencies and integration: used across x86 memory management, SEV/TDX setup, page-table creation, and random initialization. Depends on `sev_status`, `sme_me_mask`, arch random, and cc_platform attribute enums.

Risks and test signals: encryption-bit polarity differs by vendor and vTOM, so wrong mask logic exposes or corrupts memory. RDRAND failure is fatal in encrypted guests by design. Test AMD SME, SEV, SEV-ES, SNP C-bit, SNP vTOM, Intel TDX, host SNP flag set/clear, `cc_mkenc/cc_mkdec` page-table values, and RDRAND failure handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/coco/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/coco/sev/Makefile -->
# sources/distributed-fs/ceph-client/arch/x86/coco/sev/Makefile

Purpose: builds AMD SEV confidential-computing runtime support objects.

Important APIs and state: lists `core.o`, `noinstr.o`, `vc-handle.o`, and `svsm.o`. Disables UBSAN/KASAN/KCSAN/GCOV for `noinstr.o` to preserve noinstr behavior even with compiler inlining limitations.

Control flow: make-time object selection and instrumentation control only.

Dependencies and integration: feeds the AMD SEV runtime subtree used by early #VC handling, SVSM services, and CoCo platform support.

Risks and test signals: sanitizer or coverage instrumentation in noinstr code can make #VC/NMI-sensitive paths unsafe. Test sanitizer-enabled builds, objtool/noinstr validation, and SEV-ES/SNP runtime #VC paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/coco/sev/Makefile -->
