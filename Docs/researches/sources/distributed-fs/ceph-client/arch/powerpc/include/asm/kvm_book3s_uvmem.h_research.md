# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/kvm_book3s_uvmem.h

Purpose: declares Book3S secure virtual machine ultravisor memory operations and provides no-op or unsupported fallbacks when `CONFIG_PPC_UV` is disabled.

Important APIs/types/functions: enabled builds expose `kvmppc_uvmem_init/free/available`, memslot init/free/create/delete hooks, SVM hypercall handlers `kvmppc_h_svm_page_in`, `kvmppc_h_svm_page_out`, `kvmppc_h_svm_init_start/done/abort`, `kvmppc_send_page_to_uv`, and `kvmppc_uvmem_drop_pages`. Disabled builds return success for inert init/slot setup, `false` for availability, `H_UNSUPPORTED` for SVM hypercalls, and `-EFAULT` for page sending.

Control flow: KVM initialization probes ultravisor memory availability, initializes memslot metadata, and services secure-VM hypercalls by moving pages between normal guest memory and ultravisor-protected memory. Memslot deletion/drop paths can page out or discard protected pages.

State and persistence: secure page state is owned by the ultravisor and KVM memslot metadata in implementation files. This header only defines the call surface and fallback behavior.

Dependencies and integration points: depends on KVM memory slots, PPC ultravisor support, SVM hypercall return codes, and Book3S HV memory-management paths.

Risks: fallback return codes are part of guest-visible ABI; changing them can break guests probing secure VM support. Page-in/page-out operations are security-sensitive because they transfer ownership between host-visible and ultravisor-private memory.

Test signals: build with and without `CONFIG_PPC_UV`, run SVM guest initialization/page-in/page-out tests on UV-capable hardware or simulator, verify unsupported hypercalls on non-UV hosts, and test memslot add/remove cleanup of protected pages.
