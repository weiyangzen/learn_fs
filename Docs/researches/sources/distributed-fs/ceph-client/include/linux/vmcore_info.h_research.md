# sources/distributed-fs/ceph-client/include/linux/vmcore_info.h

## Purpose
`vmcore_info.h` defines the metadata note format and helper macros used to export kernel layout information to crash dump consumers. It supports kdump/vmcore tooling by recording release, build ID, page size, symbol addresses, structure sizes, offsets, lengths, constants, and config flags.

## Important APIs, Types, and Functions
Important constants are `CRASH_CORE_NOTE_*`, `CRASH_CORE_NOTE_BYTES`, `VMCOREINFO_BYTES`, `VMCOREINFO_NOTE_NAME`, and `VMCOREINFO_NOTE_SIZE`. `note_buf_t` describes per-CPU crash notes, and `crash_notes` is the per-CPU storage pointer. Declared functions include `crash_update_vmcoreinfo_safecopy()`, `crash_save_vmcoreinfo()`, `arch_crash_save_vmcoreinfo()`, `vmcoreinfo_append_str()`, `paddr_vmcoreinfo_note()`, `append_elf_note()`, `final_note()`, and optional `hwerr_log_error_type()`. Macros such as `VMCOREINFO_OSRELEASE`, `VMCOREINFO_BUILD_ID`, `VMCOREINFO_PAGESIZE`, `VMCOREINFO_SYMBOL`, `VMCOREINFO_SIZE`, `VMCOREINFO_STRUCT_SIZE`, `VMCOREINFO_OFFSET`, `VMCOREINFO_TYPE_OFFSET`, `VMCOREINFO_LENGTH`, `VMCOREINFO_NUMBER`, and `VMCOREINFO_CONFIG` serialize metadata lines into the vmcore info note.

## Control Flow
During boot or crash setup, architecture and common code append key/value metadata strings into `vmcoreinfo_data`, build an ELF note in `vmcoreinfo_note`, and expose its physical address to crash kernels. On crash, per-CPU notes capture CPU state and the second kernel combines notes when reading vmcore. Hardware error logging is compiled as a real hook only when `CONFIG_VMCORE_INFO` is enabled.

## State and Persistence
The vmcore info buffer is in-memory during the running kernel but is designed to survive into the crash dump image. Its contents become persistent only as part of a captured vmcore. Buffer sizing is fixed at one page for VMCOREINFO payload, so appenders must stay within that bound.

## Dependencies and Integration Points
The header depends on ELF core note definitions, uapi vmcore types, build ID state, physical address helpers, and architecture crash-save hooks. Integration points include kdump, `/proc/vmcore`, makedumpfile/crash tools, hardware error reporting, and architecture-specific metadata registration.

## Risks
Incorrect sizes, offsets, or symbols can make crash tools misread kernel memory. Build-ID formatting assumes a 20-byte build ID. Buffer overflow prevention depends on implementation discipline in `vmcoreinfo_append_str()`. Structure layout macros must be kept synchronized with source definitions and config combinations.

## Test Signals
Signals include kdump boot and crash capture tests, validation that `/proc/vmcore` exposes VMCOREINFO notes, crash-tool parsing of offsets/sizes, architecture metadata coverage, build-ID presence, and compile tests with and without `CONFIG_VMCORE_INFO`.
