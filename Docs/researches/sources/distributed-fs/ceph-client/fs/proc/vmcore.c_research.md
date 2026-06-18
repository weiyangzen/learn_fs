# sources/distributed-fs/ceph-client/fs/proc/vmcore.c

## Purpose
`vmcore.c` exposes the previous kernel's crash dump as `/proc/vmcore`, presenting crash-kernel ELF headers, note data, PT_LOAD memory ranges, optional device dumps, and optional device RAM as a single synthetic ELF core file.

## Important APIs, types, and functions
Global state includes `vmcore_list`, `elfcorebuf`, `elfnotes_buf`, `vmcore_size`, `proc_vmcore`, `vmcore_cb_list`, and optional `vmcoredd_list`. External APIs are `read_from_oldmem`, `register_vmcore_cb`, `unregister_vmcore_cb`, `vmcore_add_device_dump`, and `vmcore_cleanup`. Core helpers parse ELF32/ELF64 headers, merge PT_NOTE segments, rewrite PT_LOAD offsets, read or mmap old memory, and add device RAM PT_LOAD ranges.

## Control flow
`vmcore_init` asks architecture code to provide the ELF core header, validates the ELF class, reads all program headers, collapses multiple PT_NOTE headers into one page-aligned note segment, builds `vmcore_list` from PT_LOAD records, computes `vmcore_size`, and creates `/proc/vmcore`. Reads walk the synthetic layout in order: ELF header buffer, device dump notes, normal notes, then old-memory ranges. `mmap` mirrors that layout, using direct pfn remap where possible and a fault handler fallback on s390.

## State and persistence
The file is runtime state in the capture kernel, backed by memory from the crashed kernel and by vmalloc/device dump buffers. `vmcore_opened` prevents late device dump/RAM mutation from silently changing an already observed core image. SRCU-protected callbacks can mark PFNs as not RAM, causing reads and mappings to return zero pages.

## Dependencies and integration points
This code depends on crash dump boot parameters, architecture-specific oldmem helpers, ELF core validation, procfs, vmalloc, `kmsg_dump`-adjacent crash infrastructure, optional confidential-computing encrypted oldmem reads, and optional device dump/device RAM callback providers.

## Risks and test signals
Risks include malformed ELF headers, integer/rounding mistakes when rewriting note and load offsets, stale callback lifetime during read/mmap, zero-page substitution for device memory, encrypted-memory read mismatches, and late device dump insertion racing open. Test signals include ELF32 and ELF64 vmcore boot tests, sparse RAM callback tests, `/proc/vmcore` read and mmap comparison, device dump notes in crash tools, and invalid PT_NOTE truncation warnings.
