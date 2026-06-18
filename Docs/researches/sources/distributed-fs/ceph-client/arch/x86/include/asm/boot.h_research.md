
# sources/distributed-fs/ceph-client/arch/x86/include/asm/boot.h

Purpose: x86 boot/decompressor constants and prototypes shared by compressed boot code and early kernel setup.

Important APIs and control flow: defines `MIN_KERNEL_ALIGN`, validates `CONFIG_PHYSICAL_ALIGN`, selects `BOOT_HEAP_SIZE` by compressor, fixes stack and page-table allocation sizes, and defines trampoline layout constants. Declarations expose decompressor sizing symbols, `decompress_kernel()`, boot params pointer, trampoline buffer, and `trampoline_32bit_src()`.

State, dependencies, and risks: state is early boot memory, decompressor heap, boot params, and trampoline code. Dependencies include page-table types and UAPI boot definitions. Risks include too-small boot heap/page table allocations, physical alignment errors, and 5-level paging or KASLR mapping underestimation. Test signals are booting compressed kernels across compressors, KASLR, 5-level paging, and verbose boot configurations.
