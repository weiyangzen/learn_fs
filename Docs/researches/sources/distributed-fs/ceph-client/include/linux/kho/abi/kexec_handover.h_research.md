# sources/distributed-fs/ceph-client/include/linux/kho/abi/kexec_handover.h

## Purpose

`kexec_handover.h` defines the stable Kexec Handover ABI for passing preserved data from one kernel to the next. It specifies the root FDT compatible string and properties, serializable pointer macros, vmalloc preservation layouts, and radix-tree ABI nodes for preserved physical memory tracking. The source was read as a complete 289-line file.

## Important APIs, Types, and Functions

Important constants include `KHO_FDT_COMPATIBLE`, `KHO_FDT_MEMORY_MAP_PROP_NAME`, `KHO_SUB_TREE_PROP_NAME`, `KHO_SUB_TREE_SIZE_PROP_NAME`, `KHO_VMALLOC_SIZE`, and `KHO_TREE_MAX_DEPTH`. Types include `struct kho_vmalloc_hdr`, `struct kho_vmalloc_chunk`, `struct kho_vmalloc`, `enum kho_radix_consts`, `struct kho_radix_node`, and `struct kho_radix_leaf`. Helper macros are `DECLARE_KHOSER_PTR()`, `KHOSER_STORE_PTR()`, and `KHOSER_LOAD_PTR()`.

## Control Flow

The old kernel builds an FDT with physical addresses for preserved memory map data and subsystem blobs. Serializable pointers are stored as physical addresses before handover and loaded through `phys_to_virt()` by the new kernel. Vmalloc preservation walks chunks of physical page addresses; preserved-page tracking uses a multi-level page-sized radix tree with bitmap leaves.

## State and Persistence Behavior

Everything in this header is ABI state that intentionally persists across kexec. The packed physical references, page-sized chunks, and radix layout must remain interpretable by another kernel supporting the same compatible version.

## Dependencies and Integration Points

It depends on page geometry, bit helpers, log2 math, and physical/virtual address conversion. It is consumed by KHO core, preserved-memory map code, vmalloc preservation, and subsystem subtree registration.

## Risks and Edge Cases

Any incompatible FDT property, compatible string, or structure layout change requires a version bump. Pointer serialization assumes the referenced memory is preserved and identity-mappable enough for `phys_to_virt()` in the new kernel. Radix constants depend on page size and 64-bit key encoding.

## Test Signals

KHO boot/kexec handover tests, FDT compatibility validation, static structure size checks such as `kho_vmalloc_chunk == PAGE_SIZE`, radix tree encode/decode tests, and cross-version rejection tests are important.
