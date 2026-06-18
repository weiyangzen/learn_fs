<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/sgx.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/sgx.h

Purpose: Defines the Intel SGX userspace ABI for enclave creation, page addition, initialization, provisioning, SGX2 page permission/type changes, page removal, vEPC removal, and vDSO enclave entry/exit context.

Important APIs/types/functions: `enum sgx_page_flags`, `SGX_MAGIC`, `SGX_IOC_*`, `struct sgx_enclave_create`, `sgx_enclave_add_pages`, `sgx_enclave_init`, `sgx_enclave_provision`, `sgx_enclave_restrict_permissions`, `sgx_enclave_modify_types`, `sgx_enclave_remove_pages`, `sgx_enclave_user_handler_t`, `struct sgx_enclave_run`, and `vdso_sgx_enter_enclave_t`.

Control flow: Userspace opens SGX devices, issues ioctls to create an enclave, add measured pages, initialize with SIGSTRUCT, request provisioning, and optionally modify or remove pages. Enclave execution enters through the vDSO, which records exit/exception details in `sgx_enclave_run` and can invoke a user handler that chooses EENTER/ERESUME or returns to the caller.

State and persistence behavior: Enclave state persists in EPC pages and kernel enclave metadata. `sgx_enclave_run` is caller-owned transient execution state but is a stable vDSO ABI. SGX2 ioctl results include hardware ENCLS result and byte counts for partial progress.

Dependencies and integration points: Depends on Linux UAPI types/ioctl. Integrates with SGX driver, EPC management, vDSO, enclave runtimes, provisioning device, signal/exception fixups, KVM vEPC handling, and SGX2 page lifecycle.

Risks and test signals: Risks include ioctl layout drift, unsafe userspace pointer handling, partial-count mishandling, vDSO ABI misuse, and exception paths that violate x86-64 ABI assumptions. Test SGX selftests, enclave create/add/init/provision, SGX2 modify/remove flows, vDSO exception handling, user handler returns, 32-bit compat rejection/handling, and vEPC removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/sgx.h -->
