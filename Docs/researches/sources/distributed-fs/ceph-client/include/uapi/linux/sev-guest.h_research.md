<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/sev-guest.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/sev-guest.h

Purpose: defines the AMD SEV-SNP guest device ioctl ABI for attestation reports, derived keys, extended reports, and structured firmware/VMM errors.

Important APIs, types, and functions: `SNP_REPORT_USER_DATA_SIZE` sizes report nonce/user data. Request/response structs include `snp_report_req`, `snp_report_resp`, `snp_derived_key_req`, `snp_derived_key_resp`, `snp_guest_request_ioctl`, and `snp_ext_report_req`. Ioctls are `SNP_GET_REPORT`, `SNP_GET_DERIVED_KEY`, and `SNP_GET_EXT_REPORT`. Error helpers split firmware error and VMM error fields with `SNP_GUEST_FW_ERR_MASK`, `SNP_GUEST_VMM_ERR_SHIFT`, `SNP_GUEST_ERR`, and VMM error codes.

Control flow: confidential-VM userspace opens the SNP guest device, prepares a request buffer, issues an ioctl, and receives firmware-provided attestation report, derived key, or extended certificate/report material. The common ioctl wrapper carries request/response pointers and firmware error output.

State and persistence behavior: no state is stored here. Runtime state lives in the SNP guest driver, firmware mailbox, and hypervisor-mediated request path. Reports and keys are transient sensitive outputs.

Dependencies and integration points: depends on Linux types and ioctl macros. It integrates with AMD PSP/SNP firmware, confidential computing attestation agents, key derivation flows, and VMM error reporting.

Risks and edge cases: request/response pointers and lengths must be validated, extended report buffers may be too small, firmware busy/invalid-length errors need retry/reporting, and derived keys are sensitive material.

Test signals: GET_REPORT with fixed user data, derived-key requests for valid/invalid selectors, extended report buffer sizing retries, firmware and VMM error decoding, and tests in SNP guests under busy/error injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/sev-guest.h -->
