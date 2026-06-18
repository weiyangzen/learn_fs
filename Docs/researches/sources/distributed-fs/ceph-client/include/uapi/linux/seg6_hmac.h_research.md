<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/seg6_hmac.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/seg6_hmac.h

Purpose: defines SRv6 HMAC algorithm identifiers shared by userspace and kernel.

Important APIs, types, and functions: constants include `SEG6_HMAC_ALGO_SHA1`, `SEG6_HMAC_ALGO_SHA256`, and `SEG6_HMAC_ALGO_MAX`.

Control flow: userspace selects an algorithm when configuring SRv6 HMAC keys through generic netlink; packet validation/generation code uses the selected algorithm ID.

State and persistence behavior: no state is stored here. Algorithm choice is part of SRv6 HMAC key configuration.

Dependencies and integration points: integrates with `seg6_genl.h`, SRH HMAC TLVs, kernel crypto API, and iproute2.

Risks and edge cases: algorithm IDs are ABI values; adding algorithms must preserve old values. Unsupported algorithms must be rejected consistently.

Test signals: configure SHA1 and SHA256 keys, reject out-of-range IDs, and verify generated/validated HMAC TLVs match expected digest algorithms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/seg6_hmac.h -->
