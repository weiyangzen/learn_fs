# Group Research: group_576_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_sys__ddabd796fd8d

Scope checked against `Docs/research_subset_a.md`: all files are under included source tree `sources/os/illumos/illumos-gate`. Each listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dtrace.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dtrace.h

This header defines the primary DTrace kernel, provider, helper, DOF, DIF, ioctl, and ABI-facing data contracts. Although marked private to DTrace/Solaris implementation, it is the central shared definition point for kernel DTrace providers, libdtrace-facing ioctls, and embedded DOF objects.

Key contents:
- Universal DTrace constants and identifiers for probes, enabled probes, aggregations, providers, predicate caches, and name-length limits.
- DIF instruction set definitions, register/table limits, built-in variable IDs, subroutine IDs, instruction packing/extraction macros, DIF types, and DIF variable metadata.
- DTrace action classes and action IDs, including regular tracing, process actions, destructive actions, kernel actions, speculation, and aggregation actions.
- Aggregation helpers for `quantize()`, `lquantize()`, `llquantize()`, and `ustack()` packed arguments.
- DOF object format definitions: file header, section headers, section types, relocation records, option records, provider/probe records, translator records, and DIFO representation.
- Enabling description structures: probe descriptions, predicate/action/ECB descriptions, record descriptions, enabled-probe descriptions, aggregation descriptions, and format descriptions.
- Runtime option identifiers and token values for buffer policy, buffer resize policy, sizes, rates, stack frames, zone, destructive mode, and aggregation display options.
- User/kernel buffer, record, status, configuration, fault, argument-description, stability, provider-attribute, and provider-privilege structures.
- DTrace pseudodevice ioctl numbers `DTRACEIOC_*` and helper-minor ioctl numbers `DTRACEHIOC_*`.
- Helper DOF model for user-level statically defined tracing and helper actions.
- Kernel-only provider API: `dtrace_pops_t`, provider mode flags, provider registration/unregistration, probe create/lookup/fire APIs, and meta-provider APIs.
- Kernel hooks used by DTrace for virtual time, fasttrap, module load/unload, helper cleanup/fork, CPU startup, debugger integration, xcalls, toxic ranges, panic, safe signals, instruction sizing, invalid-op handling, and CPU DTrace flags.

Dependencies:
- Includes `sys/types.h`, `sys/modctl.h`, `sys/processor.h`, `sys/systm.h`, `sys/ctf_api.h`, `sys/cyclic.h`, and `sys/int_limits.h` outside `_ASM`.
- Architecture-specific sections define x86 invalid-op constants and SPARC/x86 kernel hook prototypes.
- Uses C++ guards.

Research notes:
- This is ABI-sensitive despite private-interface warnings: DOF, DIF, ioctl payloads, ELF-embedded DOF, helper DOF, and provider contracts must match libdtrace, kernel DTrace, providers, and consumers.
- Several structures are explicitly bitness-neutral or use `DTRACE_PTR()` to preserve 32-bit consumer compatibility on 64-bit kernels.
- `dtrace_probe()` is documented as callable from nearly arbitrary kernel contexts, which drives many constraints on provider callbacks and DTrace internals.
- Filesystem relevance is indirect but important: DTrace is a major observability surface for VFS, storage, page cache, ZFS, and driver code. This header defines the provider and data contracts those components use for instrumentation.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dtrace.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dtrace_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dtrace_impl.h

This header defines DTrace’s private in-kernel implementation object model. It builds on `sys/dtrace.h` and describes probes, ECBs, actions, buffers, aggregations, speculations, dynamic variables, variable state, machine state, helper state, credentials, consumer state, providers, enablings, anonymous enablings, and low-level DTrace support routines.

Key contents:
- Core typedefs and constants such as `DTRACE_MAXPROPLEN` and `DTRACE_DYNVAR_CHUNKSIZE`.
- `dtrace_probe_t`: probe identity, ECB list, provider linkage, predicate cache, artificial frames, tuple strings, and hash-chain pointers.
- Probe lookup/hash support with `dtrace_probekey_t`, `dtrace_hashbucket_t`, and `dtrace_hash_t`.
- ECB model with `dtrace_ecb_t`, `dtrace_predicate_t`, `dtrace_action_t`, and `dtrace_aggregation_t`.
- Per-CPU `dtrace_buffer_t` design for principal, aggregation, speculative, switch, ring, and fill buffers.
- Aggregation buffer metadata with `dtrace_aggkey_t` and `dtrace_aggbuffer_t`.
- Speculation state machine and `dtrace_speculation_t`.
- Dynamic variable implementation: tuple keys, dynamic variable chunks, hash buckets, per-CPU free/dirty/rinsing/clean lists, and global dynamic-state state machine.
- Variable state for statically allocated globals, thread locals, clause locals, and dynamic variables.
- Per-probe-firing machine state `dtrace_mstate_t`, including scratch state, cached args/timestamps/stack data, access flags, current DIFO, and cached `getf()` result.
- Consumer activity state machine from inactive through warmup/active/draining/cooldown/stopped/killed.
- Helper action/provider/process state and helper tracing records.
- Credential visibility/action masks and `dtrace_cred_t`.
- `dtrace_state_t`: complete in-kernel consumer state, including ECBs, buffers, speculations, aggregation arena, counters, options, credentials, cleaner/deadman cyclic IDs, and retained enabling count.
- Provider/meta-provider runtime structures and retained enabling records.
- Anonymous enabling state.
- Toxic memory range definitions.
- Architecture/platform support function prototypes for argument access, stack capture, safe copy, register access, fault reporting, atomic CAS, time, assertion failure, and SPARC/x86-specific helpers.
- DTrace-local `ASSERT`/`VERIFY` overrides safe for probe context.

Dependencies:
- Includes `sys/dtrace.h`.
- Assumes kernel types such as `cred_t`, `file_t`, `vmem_t`, `cyclic_id_t`, `kthread_t`, `proc_t`, `pc_t`, `greg_t`, and `struct regs`.

Research notes:
- This is kernel-private and tightly coupled to `uts/common/os/dtrace.c` and ISA-specific DTrace code.
- The comments document major correctness constraints: per-CPU buffers to avoid sharing, atomic buffer switching with interrupts disabled, ring-buffer oldest-record tracking, nonblocking scratch allocation, asynchronous speculation cleanup, and dynamic-variable dirty/rinsing cleanup via `dtrace_sync()`.
- Dynamic variables deliberately avoid immediate chunk reuse to prevent cross-CPU stale references from observing unrelated new values.
- Filesystem relevance is observability and debugging: this is the implementation state behind DTrace probes that filesystem, VM, and storage code may fire or depend on for diagnostics.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dtrace_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dumpadm.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dumpadm.h

This small header defines the `/dev/dump` ioctl command namespace and dump configuration flags used by dump administration tools and kernel dump configuration code.

Key contents:
- Dump ioctl base `DDIOC`.
- `/dev/dump` ioctls:
  - `DIOCGETDUMPSIZE`
  - `DIOCGETCONF`
  - `DIOCSETCONF`
  - `DIOCGETDEV`
  - `DIOCSETDEV`
  - `DIOCTRYDEV`
  - `DIOCDUMP`
  - `DIOCSETUUID`
  - `DIOCGETUUID`
  - `DIOCRMDEV`
- Kernel-controlled dump state flags:
  - `DUMP_EXCL`
  - `DUMP_STATE`
- User-controlled mutually exclusive dump content flags:
  - `DUMP_KERNEL`
  - `DUMP_ALL`
  - `DUMP_CURPROC`
  - `DUMP_CONTENT`

Dependencies:
- No included headers.
- Uses C++ guards.

Research notes:
- This is a device-control ABI for dump configuration.
- Its content flags mirror the crash dump content flags in `dumphdr.h`.
- Filesystem/storage relevance is direct: dump configuration selects and controls the dump device, often a disk/swap-backed storage target.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dumpadm.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dumphdr.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dumphdr.h

This header defines the on-device crash dump header format, dump metadata structures, compression stream metadata, and kernel dump subsystem entry points.

Key contents:
- Dump constants: magic, version, word size, panic string size, conservative compression ratio, device padding offset, saved log area size, ereport area size, and summary area size.
- `dumphdr_t`: crash dump header containing offsets to symbols, PFN table, translation map, dump data, utsname/platform/panic/time metadata, page geometry, hash metadata, page counts, symbol sizes, fault-management panic flag, and OS image UUID.
- Dump validity/content flags:
  - `DF_VALID`
  - `DF_COMPLETE`
  - `DF_LIVE`
  - `DF_COMPRESSED`
  - `DF_KERNEL`
  - `DF_ALL`
  - `DF_CURPROC`
  - `DF_CONTENT`
- `dump_map_t` and `DUMP_HASH()` for translating address-space/virtual-address pairs to dump data offsets.
- Compressed-size/tag word encoding helpers:
  - `DUMP_SET_TAG`
  - `DUMP_GET_TAG`
  - `DUMP_SET_CSIZE`
  - `DUMP_GET_CSIZE`
- Parallel dump stream metadata `dumpstreamhdr_t` and stream magic `DUMP_STREAM_MAGIC`.
- Data-header metadata `dumpdatahdr_t`, magic/version constants, and compression-level constants for LZJB and bzip2.
- Kernel-only globals for dump vnode, dump size, dump header, config flags, path, timeout/error state, and platform CPU thresholds.
- Kernel dump functions such as `dumpinit`, `dumpfini`, `dump_resize`, `dump_page`, `dump_addpage`, `dumpsys`, helper variants, log/ereport dump routines, dump device writes/resizing, platform dump hooks, and UUID accessors.
- Dump-page reservation helpers and `IS_DUMP_PAGE()`.

Dependencies:
- Includes `sys/types.h`, `sys/param.h`, `sys/utsname.h`, and `sys/log.h`.
- Kernel section depends on vnode, mutex, PFN/page, and address-space types.
- Uses C++ guards.

Research notes:
- The file documents the two-header dump layout: one header at the beginning and a terminal header at the end of the dump device.
- Struct layout and constants are savecore/dumpsys compatibility boundaries.
- Storage relevance is direct: this describes how kernel memory images are laid out on dump devices and how compressed dump streams are interpreted.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dumphdr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/edonr.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/edonr.h

This header declares the Edon-R hash implementation interface and state layout, adapted from a NIST/SUPERCOP-style implementation.

Key contents:
- Digest and block sizes for EdonR-224, EdonR-256, EdonR-384, and EdonR-512.
- Block bit sizes for 256-bit and 512-bit variants.
- Internal state structs:
  - `EdonRData256`
  - `EdonRData512`
  - `EdonRState`
- Public hash API:
  - `EdonRInit`
  - `EdonRUpdate`
  - `EdonRFinal`
  - `EdonRHash`

Dependencies:
- Includes `sys/types.h`.
- Uses fixed-width integer types and `size_t`.
- Uses C++ guards.

Research notes:
- The comment warns that consecutive `EdonRUpdate()` calls are constrained by the amount of unprocessed plus newly supplied data relative to the compression block size; otherwise an assertion failure is invoked.
- Filesystem relevance is likely through checksum/hash consumers, especially storage code that can use Edon-R as an algorithm primitive.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/edonr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/efi.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/efi.h

This header defines UEFI GUIDs, memory-map data types, EFI memory descriptors, and 32-bit/64-bit EFI system table layouts based on UEFI specification data.

Key contents:
- EFI configuration table GUID macros for global variables, MPS, ACPI, SMBIOS/SMBIOS3, SAL, FDT, DXE services, HOB list, memory type information, debug image info, and EFI properties.
- `efi_guid_t` as an aligned `struct uuid`.
- EFI physical and virtual address typedefs.
- `EFI_MEMORY_TYPE` enum including loader, boot services, runtime services, conventional, unusable, ACPI, MMIO, PAL, persistent, and unaccepted memory types.
- EFI memory attribute bits for caching, write/read/execute protection, nonvolatile/more-reliable/read-only memory, and runtime mapping.
- `EFI_MEMORY_DESCRIPTOR`.
- `EFI_TABLE_HEADER`.
- Revision helpers `EFI_REV`, `EFI_REV_MAJOR`, and `EFI_REV_MINOR`.
- EFI system table signature.
- 32-bit and 64-bit pointer typedefs plus packed configuration table and system table layouts:
  - `EFI_CONFIGURATION_TABLE32`
  - `EFI_CONFIGURATION_TABLE64`
  - `EFI_SYSTEM_TABLE32`
  - `EFI_SYSTEM_TABLE64`

Dependencies:
- Includes `sys/uuid.h`.
- Uses packed/aligned attributes.
- Uses C++ guards.

Research notes:
- This is firmware ABI layout, so packing and field widths are critical.
- `EFI_REV(x, y)` uses logical OR in the macro body rather than bitwise OR; readers should preserve existing behavior unless intentionally fixing ABI-facing code.
- Filesystem/storage relevance is boot and platform discovery: EFI memory and table parsing supports boot-time device/platform setup, while GPT handling is in `efi_partition.h`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/efi.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/efi_partition.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/efi_partition.h

This header defines the on-disk GPT/EFI partition structures, well-known partition type GUIDs, Solaris GPT abstraction structures, and userland libefi helper prototypes.

Key contents:
- GPT label constants, GPT signature, EFI header size workaround, and reserved padding size calculation.
- On-disk little-endian GPT header `efi_gpt_t`.
- GPT entry attribute bitfield `efi_gpe_Attrs_t`.
- Partition type GUID macros for Solaris/illumos partition roles, EFI system/legacy MBR, Symantec, Microsoft reserved, Dell, Apple HFS/UFS/ZFS/APFS, FreeBSD boot/swap/UFS/Vinum/ZFS, and BIOS boot.
- Minimum partition array and reserved partition sizes.
- GPT partition entry `efi_gpe_t`.
- Solaris library partition abstraction `dk_part_t`.
- Solaris GPT abstraction `dk_gpt_t`, including version, partition count, LBA sizing/bounds, disk GUID, flags, alternate LBA, and flexible partition array.
- GPT corruption flag `EFI_GPT_PRIMARY_CORRUPT`.
- Private libefi/driver ioctl payload `dk_efi_t`.
- 64-bit partition descriptor `partition64`.
- `EFI_NUMPAR`.
- Userland libefi prototypes under `!_KERNEL`: allocation, read, write, free, type, error check, auto sense, reserved sectors, and whole-disk helpers.

Dependencies:
- Includes `sys/uuid.h` and `sys/stddef.h`.
- Uses `diskaddr_t`, `uint_t`, `ushort_t`, and `len_t`.
- Uses C++ guards.

Research notes:
- The comment explains that some AMI EFI firmware expects the header size to be 92 bytes rather than `sizeof (efi_gpt_t)`, so `EFI_HEADER_SIZE` intentionally stops before reserved padding.
- The header bridges on-disk GPT structures and Solaris VTOC-like abstractions used by libefi and drivers.
- Filesystem/storage relevance is direct: this is the partition-table format used to discover and manage disk slices/partitions for filesystems and block devices.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/efi_partition.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/elf.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/elf.h

This header defines the generic ELF object-file ABI used by illumos for executables, shared objects, relocatable objects, core files, notes, capabilities, and architecture extension inclusion.

Key contents:
- File-size constants for ELF32 and ELF64 scalar types.
- ELF header layouts `Elf32_Ehdr` and conditionally `Elf64_Ehdr`.
- ELF identification indexes, magic constants, class/data/version/OSABI/ABI-version constants, file types, machine IDs, and object version constants.
- Extensive `EM_*` machine registry through current values such as RISC-V, BPF, LoongArch, and newer assigned machine IDs.
- Program header layouts `Elf32_Phdr` and `Elf64_Phdr`.
- Program header types including standard `PT_*`, Sun extensions, GNU compatibility values, stack/capability/DTrace segments, and processor ranges.
- Program header flags, including Solaris core-dump failure/killed/siginfo flags and extended program header index.
- Section header layouts `Elf32_Shdr` and `Elf64_Shdr`.
- Section types, Solaris ABI-specific section types, GNU overlapping OSABI-specific types, LLVM section extensions, processor/user ranges, section flags, and reserved section indexes.
- Symbol table layouts `Elf32_Sym` and `Elf64_Sym`, symbol info macros, binding/type/visibility constants.
- Relocation layouts `Elf32_Rel`, `Elf32_Rela`, `Elf64_Rel`, and `Elf64_Rela`, plus relocation info macros and SPARC V9 type-data helpers.
- Section group flag `GRP_COMDAT`.
- Note headers `Elf32_Nhdr` and `Elf64_Nhdr`.
- Move entries and move info macros.
- Capability entries, capability info/chain typedefs, capability info macros, capability section versions, capability group constants, Sun capability tags, and software capability bits.
- Core-note type constants for proc status, fpreg, psinfo, auxv, SPARC windows, LDT, pstatus, credentials, utsname, LWP data, privileges, core content, zone name, fd info, security flags, LWP name, user panic, and cwd.
- Kernel `elfheadcheck()` prototype.
- Conditional inclusion of `elf_SPARC.h`, `elf_386.h`, and `elf_amd64.h`.

Dependencies:
- Includes `sys/elftypes.h`.
- Uses C++ guards.
- 64-bit definitions require `_LP64` or `_LONGLONG_TYPE`.

Research notes:
- This is a core ABI header for the runtime linker, kernel exec/core handling, link-editor tooling, debuggers, and object-file consumers.
- Some Solaris and GNU section/program values overlap, and comments explicitly require OSABI knowledge for correct interpretation.
- The DTrace relationship appears through `SHT_SUNW_dof` and `PT_SUNWDTRACE`.
- Filesystem relevance is indirect but foundational: filesystems store ELF binaries and core files, while the kernel uses these structures during exec and core dump generation.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/elf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/elf_386.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/elf_386.h

This header defines i386-specific ELF relocation values, maximum page size, section flags/indexes, and PLT/GOT layout constants.

Key contents:
- `R_386_*` relocation constants, including absolute/PC-relative, GOT/PLT, copy/global/jump slot/relative, TLS models, descriptor TLS, `IRELATIVE`, and `GOT32X`.
- `R_386_NUM`.
- `ELF_386_MAXPGSZ`.
- Processor-specific section flags and reserved section indexes:
  - `SHF_ORDERED`
  - `SHF_EXCLUDE`
  - `SHN_BEFORE`
  - `SHN_AFTER`
- Architecture-common guard `_SYS_ELF_MACH_COMMON` and marker `_SYS_ELF_MACH_386`.
- i386 PLT/GOT constants:
  - `M_PLT_INSSIZE`
  - `M_PLT_XNumber`
  - `M_GOT_XDYNAMIC`
  - `M_GOT_XLINKMAP`
  - `M_GOT_XRTLD`
  - `M_GOT_XNumber`
  - 32-bit word/PLT/GOT alignment, entry sizes, and reserved PLT size.
- Common aliases for non-`_ELF64` builds.

Dependencies:
- No includes of its own.
- Uses C++ guards.

Research notes:
- This file is included by `elf_amd64.h`, so it uses guards to avoid conflicts when architecture headers are included together.
- Constants are ABI-sensitive for link-editing, relocation processing, and runtime linker behavior.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/elf_386.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/elf_SPARC.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/elf_SPARC.h

This header defines SPARC-specific ELF flags, relocations, section/symbol/dynamic values, register symbol numbers, and PLT/GOT layout constants for 32-bit and 64-bit SPARC.

Key contents:
- SPARC `e_flags` masks and values for V8+ and vendor extensions.
- SPARC V9 memory model flags for TSO, PSO, and RMO.
- `R_SPARC_*` relocation constants from basic relocations through 64-bit, TLS, GOT-data, size, and `H34`; plus `R_SPARC_NUM`.
- Alias `R_SPARC_L34`.
- SPARC and SPARCV9 maximum page sizes.
- Processor-specific section type `SHT_SPARC_GOTDATA`.
- Section flags/indexes `SHF_ORDERED`, `SHF_EXCLUDE`, `SHN_BEFORE`, and `SHN_AFTER`.
- SPARC register symbol type and dynamic tag:
  - `STT_SPARC_REGISTER`
  - `DT_SPARC_REGISTER`
- Register symbol numbers for `%g1` through `%g7`.
- Architecture-common PLT/GOT constants:
  - PLT instruction size and reserved counts.
  - GOT dynamic entry index.
  - 32-bit PLT/GOT alignment and entry sizes.
  - 64-bit PLT/GOT alignment, entry sizes, near/far PLT sizing, and far PLT block constants.
- Common aliases selected by `_ELF64`.

Dependencies:
- No includes of its own.
- Uses C++ guards.

Research notes:
- Like the x86 ELF headers, this is consumed by linkers, runtime linkers, loaders, and debuggers.
- The `_SYS_ELF_MACH_COMMON` guard prevents conflicting generic `M_*` definitions when multiple architecture headers are included.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/elf_SPARC.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/elf_amd64.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/elf_amd64.h

This header defines AMD64/x86-64-specific ELF relocation constants, aliases, maximum page size, section/index flags, and 64-bit PLT/GOT layout details.

Key contents:
- Includes `sys/elf_386.h` for shared x86 definitions.
- `R_AMD64_*` relocation constants including absolute, PC-relative, GOT/PLT, copy/global/jump slot/relative, TLS, size, descriptor TLS, `IRELATIVE`, `RELATIVE64`, GOTPCRELX, and REX_GOTPCRELX.
- Compatibility aliases mapping `R_X86_64_*` names to `R_AMD64_*`.
- `ELF_AMD64_MAXPGSZ`.
- Processor-specific section type `SHT_AMD64_UNWIND` and alias `SHT_X86_64_UNWIND`.
- Large-section flags and common aliases:
  - `SHF_AMD64_LARGE`
  - `SHF_X86_64_LARGE`
- Large common section indexes:
  - `SHN_AMD64_LCOMMON`
  - `SHN_X86_64_LCOMMON`
- 64-bit PLT/GOT constants when `elf_386.h` established the x86 common block.
- Common `M_*` aliases for `_ELF64`.

Dependencies:
- Includes `sys/elf_386.h`.
- Uses C++ guards.

Research notes:
- Maintains both Solaris `R_AMD64_*` and System V AMD64 psABI `R_X86_64_*` names for compatibility.
- `PT_SUNW_UNWIND` is intentionally defined in the generic OS-specific range in `elf.h`.
- ABI-sensitive for link-editor/runtime-linker relocation behavior.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/elf_amd64.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/elf_notes.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/elf_notes.h

This small header defines Sun-specific ELF note naming and a note type for page-size hints.

Key contents:
- ELF note owner/name string:
  - `ELF_NOTE_SOLARIS`
- Note type:
  - `ELF_NOTE_PAGESIZE_HINT`

Dependencies:
- No includes.
- Uses C++ guards.

Research notes:
- `ELF_NOTE_PAGESIZE_HINT` describes the desired page size for ELF `PT_LOAD` segments; the descriptor is one word containing the desired page size.
- This is a small ABI helper for ELF producers/consumers that understand Solaris notes.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/elf_notes.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/elftypes.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/elftypes.h

This header defines the base fixed-width-ish ELF scalar typedefs used by `sys/elf.h`.

Key contents:
- `Elf32_*` typedefs:
  - `Elf32_Addr`
  - `Elf32_Half`
  - `Elf32_Off`
  - `Elf32_Sword`
  - `Elf32_Word`
- `Elf64_*` typedefs under `_LP64` or `_LONGLONG_TYPE`:
  - `Elf64_Addr`
  - `Elf64_Half`
  - `Elf64_Off`
  - `Elf64_Sword`
  - `Elf64_Sxword`
  - `Elf64_Word`
  - `Elf64_Xword`
  - `Elf64_Lword`
  - `Elf32_Lword`

Dependencies:
- Includes `sys/feature_tests.h`.
- Uses C++ guards.

Research notes:
- Typedef choices vary by compilation model so that ELF32 types have the expected ABI size on both LP64 and non-LP64 builds.
- This is foundational ABI plumbing for all ELF structure definitions.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/elftypes.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/emul64.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/emul64.h

This header defines ioctl commands and payloads for the `emul64` SCSI adapter emulator test driver, mainly for manipulating large emulated device ranges and injecting errors.

Key contents:
- `EMUL64IOC` ioctl base.
- Ioctls:
  - `EMUL64_WRITE_OFF`
  - `EMUL64_WRITE_ON`
  - `EMUL64_ZERO_RANGE`
  - `EMUL64_ERROR_INJECT`
- Block range structure `emul64_range_t`.
- Target/LUN-specific range structure `emul64_tgt_range_t`.
- Error injection states:
  - `ERR_INJ_DISABLE`
  - `ERR_INJ_ENABLE`
  - `ERR_INJ_ENABLE_NODATA`
- Error injection payload `emul64_error_inj_data`, including target/LUN, injection state, sense data length, SCSI status, packet reason, and packet state.

Dependencies:
- Includes `sys/inttypes.h`, `sys/types.h`, and `sys/scsi/scsi.h`.
- Uses `diskaddr_t`, `struct scsi_status`, and SCSI packet status fields.
- Uses C++ guards.

Research notes:
- The file documents three original testing ioctls for ignoring writes, enabling writes, and zeroing ranges; the header also includes an error-injection ioctl.
- Storage relevance is direct for test infrastructure: it lets tests accelerate large-device operations or simulate SCSI behavior without real media changes.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/emul64.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/emul64cmd.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/emul64cmd.h

This header defines per-command private data and command flags for the `emul64` SCSI adapter emulator driver.

Key contents:
- Packet/private-data conversion macros:
  - `PKT2CMD(pkt)`
  - `CMD2PKT(sp)`
- `struct emul64_cmd`: per-command state allocated with `scsi_pkt`, including packet pointer, queue link, buffer address, completion deadline, flags, byte count, CDB/SCB lengths, and owning `emul64` instance pointer.
- Command flags:
  - `CFLAG_FINISHED`
  - `CFLAG_COMPLETED`
  - `CFLAG_IN_TRANSPORT`
  - `CFLAG_TRANFLAG`
  - `CFLAG_DMAVALID`
  - `CFLAG_DMASEND`
  - `CFLAG_CMDIOPB`
  - `CFLAG_FREE`
  - `CFLAG_DMA_PARTIAL`

Dependencies:
- Includes `sys/scsi/scsi_types.h`.
- Depends on `struct scsi_pkt` and forward-declared `struct emul64`.
- Uses C++ guards.

Research notes:
- This is driver-private SCSI transport bookkeeping, not a general user ABI.
- The flags separate transport lifecycle state from DMA and allocation/free-list state.
- Storage relevance is direct to the emulated SCSI HBA path used for block-device testing.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/emul64cmd.h -->