## sources/distributed-fs/ceph-client/arch/arm64/kernel/vdso.c

### Purpose
`vdso.c` validates, initializes, and maps ARM64 VDSO/VVAR pages for native AArch64 tasks and optional AArch32 compat tasks, including compat signal and kuser helper pages.

### Important APIs, Types, And Functions
Key APIs are `arch_setup_additional_pages`, `aarch32_setup_additional_pages`, `vdso_init`, `aarch32_alloc_vdso_pages`, `__vdso_init`, and `__setup_additional_pages`. It defines `struct vdso_abi_info`, AArch64 and AArch32 `vm_special_mapping` descriptors, and mremap callbacks.

### Control Flow
Boot-time init checks the embedded VDSO ELF magic, computes page count, allocates a page-list array, translates embedded PFNs to pages, and installs them into the mapping descriptor. Exec-time setup takes the mmap write lock, reserves a contiguous VVAR plus VDSO region, installs VVAR, records `mm->context.vdso`, and installs executable sealed special mapping with BTI flags when supported. Compat setup may also install kuser helper vectors, a poisoned sigreturn page, optional compat VDSO, and `mm->context.sigpage`.

### State, Persistence, And Dependencies
State includes `vdso_info`, special mapping page lists, `aarch32_vectors_page`, `aarch32_sig_page`, `mm->context.vdso`, and `mm->context.sigpage`. Mapping state persists for the life of each process mm.

### Integration Points
The file connects exec, mmap, VVAR data pages, VDSO binaries from `vdso-wrap.S` and `vdso32-wrap.S`, compat signal handling, kuser helpers, BTI, and generic special mapping logic.

### Risks
Mapping order and lengths are ABI-visible. Missing ELF validation, wrong page counts, or bad mremap updates can leave userspace with broken VDSO pointers. Compat vectors intentionally avoid writable mappings for ARM ABI safety, while sigpage permits COW for debuggers.

### Test Signals
Run native and compat process exec tests, VDSO symbol calls, ASLR/mremap of `[vdso]` and `[sigpage]`, BTI-enabled execution, kuser-helper compatibility, and failure injection for page allocations.
