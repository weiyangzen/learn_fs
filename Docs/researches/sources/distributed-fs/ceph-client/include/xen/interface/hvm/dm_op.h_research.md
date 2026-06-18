# sources/distributed-fs/ceph-client/include/xen/interface/hvm/dm_op.h

Purpose: defines the generic buffer descriptor used by Xen HVM device-model operations. The file is deliberately small and supplies ABI layout only.

Important APIs/types/functions: `struct xen_dm_op_buf` contains a guest handle `h` and a `xen_ulong_t size`. `DEFINE_GUEST_HANDLE_STRUCT(xen_dm_op_buf)` exports the type for hypercall argument handling.

Control flow: higher-level HVM device-model hypercalls pass one or more `xen_dm_op_buf` descriptors to describe guest-visible buffers. This header does not define operation numbers; it only defines the payload wrapper.

State and persistence: there is no persistent local state. The buffer points to caller-owned memory for the duration of a device-model operation.

Dependencies and integration points: depends on Xen public handle macros and `xen_ulong_t` being available from already included Xen headers. Integrates with userspace or toolstack device models that marshal buffers into Xen hypercalls.

Risks: ABI width depends on `xen_ulong_t`, so callers must use the ABI selected for the guest/toolstack interface. Bad `size` values can truncate or overrun operation payloads if not validated by the caller and hypervisor.

Test signals: compile tests for both 32-bit and 64-bit ABI consumers, hypercall smoke tests using empty and non-empty buffers, and negative tests for invalid guest handles or sizes.
