# sources/distributed-fs/ceph-client/include/uapi/linux/nsm.h

Purpose: Defines the ioctl ABI for AWS Nitro Secure Module raw message exchange.

Important APIs/types/functions: Exports `NSM_MAGIC`, `NSM_REQUEST_MAX_SIZE`, `NSM_RESPONSE_MAX_SIZE`, `struct nsm_iovec`, `struct nsm_raw`, and `NSM_IOCTL_RAW`. `struct nsm_iovec` carries a userspace virtual address and length as 64-bit fields; `struct nsm_raw` pairs request and response buffers.

Control flow: A privileged userspace process opens the NSM device and submits `NSM_IOCTL_RAW` with request and response iovecs. The driver copies or maps the request, sends it to the Nitro Secure Module, then fills the response buffer subject to maximum sizes.

State and persistence behavior: The header defines transient request/response buffers only. Persistent attestation keys, entropy state, and module state live in the platform device or firmware, not in this ABI header.

Dependencies and integration points: Depends on `<linux/ioctl.h>` and `<linux/types.h>`. Integrates with enclave attestation agents and Nitro platform drivers. The comment notes raw access is gated by `CAP_SYS_ADMIN`.

Risks: User pointers and lengths are untrusted; kernel handling must enforce request and response maxima and avoid leaking stale response bytes. Because raw messages can affect attestation or key operations, capability and device access policy are high-impact.

Test signals: Build 32/64-bit userspace clients, submit boundary-size requests, verify response truncation/error behavior, test invalid pointers and over-limit lengths, and confirm unprivileged callers cannot use the raw ioctl.
