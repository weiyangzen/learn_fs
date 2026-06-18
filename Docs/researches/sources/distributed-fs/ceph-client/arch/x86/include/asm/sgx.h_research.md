<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/sgx.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/sgx.h

Purpose: defines Intel SGX architectural structures and Linux SGX helper declarations. Important definitions include SGX CPUID leaves, ENCLS function numbers, ENCLS fault flag, return codes, `sgx_miscselect`, SGX attributes and masks, `sgx_secs`, `sgx_tcs`, `sgx_pageinfo`, page/secinfo types, `sgx_secinfo`, `sgx_pcmd`, `sgx_sigstruct`, KVM virtualization hooks, and `sgx_set_attribute()`.

Control flow: SGX driver and KVM code use these layouts to create enclaves, add/extend pages, initialize signatures, swap EPC pages, virtualize ECREATE/EINIT, and enforce allowed attributes. ENCLS return/fault encoding is normalized with `SGX_ENCLS_FAULT_FLAG` so callers can distinguish SGX positive status, CPU faults, and Linux errors.

State and persistence: SGX enclave state resides in EPC pages and metadata described by SECS/TCS/SECINFO/PCMD; swapped pages carry PCMD integrity data in regular memory. The header itself declares ABI layouts rather than owning state.

Dependencies include SGX CPU architecture, KVM SGX virtualization, user ioctl structures, EPC management, RSA/signature validation, and xsave attribute masks. Risks include packed layout drift, reserved-bit validation errors, wrong fault-code mapping, and privilege mistakes around provisioning/token keys. Test signals include SGX selftests, enclave create/init/run, EPC reclaim/load, KVM SGX ECREATE/EINIT, invalid attribute masks, and ENCLS fault-path coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/sgx.h -->
