# sources/distributed-fs/ceph-client/drivers/virt/coco/sev-guest/sev-guest.c

## Purpose
Provides AMD SEV-SNP guest userspace and TSM interfaces for attestation reports, derived keys, extended reports with certificates, and optional SVSM service attestation.

## APIs, Types, and Functions
Core state is `struct snp_guest_dev` with a device, miscdevice, and `struct snp_msg_desc`. Important functions are `snp_guest_ioctl()`, `get_report()`, `get_derived_key()`, `get_ext_report()`, `sev_report_new()`, `sev_svsm_report_new()`, visibility callbacks, `sev_guest_probe()`, and `sev_guest_remove()`. It exposes `/dev/sev-guest` ioctls `SNP_GET_REPORT`, `SNP_GET_DERIVED_KEY`, and `SNP_GET_EXT_REPORT`, and registers `sev_tsm_report_ops`.

## Control Flow and State
Probe requires `CC_ATTR_GUEST_SEV_SNP`, allocates and initializes the SNP message descriptor using `vmpck_id`, registers TSM ops, then registers the misc device. Ioctls copy a common request struct, require nonzero message version, and dispatch to encrypted SNP guest requests. Extended reports allocate a shared decrypted certificate buffer when requested, send a VMGEXIT extended guest request, copy certs and report back, and restore encryption before freeing. TSM report generation either calls SVSM attestation when `service_provider=svsm` or issues an SNP extended report, validates the response header, copies the report into `outblob`, and optionally exposes certificate data as `auxblob`.

## Dependencies and Integration
Depends on AMD SNP guest messaging (`snp_msg_*`, `snp_send_guest_request()`), SEV/SVM VMGEXIT definitions, memory encryption transitions, miscdevice, configfs TSM, and optional SVSM attestation helpers.

## Risks and Test Signals
Risks are sensitive derived-key buffer wiping, shared-page encryption restoration failures, certificate-size truncation, VMPCK selection and invalid-key handling, and provider registration ordering before `snp_dev->msg_desc` assignment. Tests should cover all ioctls, bad user pointers, zero message version, invalid cert lengths, VMM invalid-length feedback, SVSM retry resizing, TSM attr visibility under VMPL, and cleanup on probe failure.
