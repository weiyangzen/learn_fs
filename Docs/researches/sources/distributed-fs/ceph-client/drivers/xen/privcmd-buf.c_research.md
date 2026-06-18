# sources/distributed-fs/ceph-client/drivers/xen/privcmd-buf.c

Purpose: implements mmap support for Xen privcmd hypercall buffers, exposing shared, zeroed kernel pages through the `xen/hypercall` misc device object declared here.

Important APIs/functions: exports `xen_privcmdbuf_fops` and defines `xen_privcmdbuf_dev`. File and VMA operations are `privcmd_buf_open`, `privcmd_buf_release`, `privcmd_buf_mmap`, `privcmd_buf_vma_open`, `privcmd_buf_vma_close`, and `privcmd_buf_vma_fault`. Core types are `struct privcmd_buf_private` and `struct privcmd_buf_vma_private`.

Control flow: open allocates per-file state and a VMA list. `mmap` requires `VM_SHARED`, allocates one zeroed page per VMA page, creates VMA-private metadata, sets `VM_IO | VM_DONTEXPAND`, maps pages with `vm_map_pages_zero`, and links the allocation into the file list. VMA open/close refcount duplicated mappings. Release frees all remaining VMA-private allocations and pages. Faults return `VM_FAULT_SIGBUS`, because all valid pages are pre-mapped.

State and persistence: per-file state owns a mutex and list of VMA allocations. Each VMA allocation stores page array, page count, and user count. Pages persist until the last VMA reference closes or the file is released.

Dependencies and integration: included by the Xen privcmd driver through `privcmd.h`, uses Linux miscdevice/file/VM APIs, and exports file operations for registration elsewhere.

Risks: mappings must be shared; partial allocation failure frees the VMA allocation while still under setup; release forcibly frees all tracked mappings for the file; no demand fault recovery is supported beyond SIGBUS.

Test signals: mmap shared hypercall buffers of multiple pages, fork/duplicate VMAs to exercise open/close users, close file before/after munmap, test private mmap rejection, injected page allocation failure, and fault outside mapped pages.
