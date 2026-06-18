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
