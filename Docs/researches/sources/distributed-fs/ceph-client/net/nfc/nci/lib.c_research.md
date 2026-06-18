# sources/distributed-fs/ceph-client/net/nfc/nci/lib.c

Purpose: Provides a shared translation from NCI status codes to Linux errno values.

Important APIs and functions: `nci_to_errno` maps `NCI_STATUS_OK` to 0, protocol and parameter errors to `-EPROTO`, controller busy/rejected states to `-EBUSY`, timeout/transmission errors to timeout/communication errno values, and unknown/failure statuses to `-ENOSYS`. It is exported for NCI core and drivers.

Control flow: Simple switch over the controller status byte. It is used when request completion status is converted by `__nci_request` and when data-frame status bytes are processed.

State and persistence: No state.

Dependencies and integration points: Includes NCI public and core headers for status constants and is linked into the core `nci` module.

Risks: Any new NCI status codes not mapped here will collapse to `-ENOSYS`, which may obscure the failure cause. Some mappings are policy choices and should match userspace expectations.

Test signals: Unit-style tests for every known status code, unknown status fallback, and callers that compare exact errno values.
