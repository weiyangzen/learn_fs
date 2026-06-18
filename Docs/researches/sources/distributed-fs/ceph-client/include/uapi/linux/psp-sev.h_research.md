<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/psp-sev.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/psp-sev.h

Purpose: defines the AMD SEV/SNP platform management userspace ABI for PSP firmware commands, return codes, certificates, platform status, firmware IDs, and SNP configuration.

Important APIs and types: command enum includes factory reset, platform status, PEK/PDH generation and certificate operations, deprecated and current ID retrieval, SNP platform status, commit, set config, and VLEK load. `sev_ret_code` lists firmware and wrapper errors. Packed structs include platform status, PEK CSR/import/export buffers, ID retrieval, SNP status/config/commit/VLEK payloads, and the top-level `struct sev_issue_cmd` used by the ioctl. The ioctl family is typically exposed through `/dev/sev` with command ID, data pointer, and firmware error reporting.

Control flow: userspace management tools build a command-specific packed payload, wrap it in the issue-command structure, and call the SEV ioctl. The kernel validates user buffers, serializes PSP mailbox access, invokes firmware, copies output fields, and reports both syscall errno and SEV firmware status.

State and persistence: state is PSP firmware/platform SEV state: ownership, certificates, platform config, guest count, SNP state, VLEK material, and firmware identity. Certificate and ownership state can persist across boots or until factory reset depending on platform firmware.

Dependencies and integration points: depends on Linux integer types and packed ABI layout. Integrates with AMD PSP, KVM SEV/SNP guest launch infrastructure, attestation/certificate tooling, firmware update/ownership workflows, and cloud confidential-computing management.

Risks and test signals: risks include destructive factory reset/commit operations, certificate buffer length races, packed alignment/compat issues, firmware error propagation, and SNP config policy mistakes. Test status and cert export/import, small/large buffers, deprecated `GET_ID` handling, SNP status/config flows, concurrent command serialization, and negative firmware return codes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/psp-sev.h -->
