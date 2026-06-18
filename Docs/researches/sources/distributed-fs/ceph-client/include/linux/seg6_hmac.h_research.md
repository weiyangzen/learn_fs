# sources/distributed-fs/ceph-client/include/linux/seg6_hmac.h

Purpose: `seg6_hmac.h` wraps UAPI definitions for SRv6 HMAC configuration.

Important APIs/types/functions: It includes `<uapi/linux/seg6_hmac.h>` and declares no additional helpers.

Control flow: No executable code is present. SRv6 HMAC code consumes the UAPI constants and structures to configure authentication keys/algorithms.

State and persistence behavior: Key and policy state are owned by SRv6 networking code, not this wrapper.

Dependencies and integration points: It integrates with IPv6 segment-routing HMAC validation, netlink configuration, and crypto algorithm selection.

Risks: UAPI drift can break userspace configuration. HMAC key handling must be implemented outside this header with proper secret lifetime controls.

Test signals: Netlink HMAC key configuration, packet validation with matching and failing HMACs, disabled SRv6-HMAC configs, and userspace ABI compatibility.
