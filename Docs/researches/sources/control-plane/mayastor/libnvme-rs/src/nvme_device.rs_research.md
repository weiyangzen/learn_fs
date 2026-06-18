# sources/control-plane/mayastor/libnvme-rs/src/nvme_device.rs

Purpose: plain Rust data model for an NVMe namespace/block device discovered through libnvme.

Important APIs/types/functions: `NvmeDevice` has `namespace`, `device`, `firmware`, `model`, `serial`, `utilisation`, `max_lba`, `capacity`, and `sector_size`, and derives `Clone` and `Debug`.

Control flow: none; instances are constructed by `NvmeTarget::get_device_from_ns`.

State/persistence: snapshot of kernel/libnvme namespace metadata at discovery time.

Dependencies/integration: returned by `NvmeTarget::list` and likely consumed by tests that need to find Mayastor NVMe devices.

Risks: fields are public and unvalidated; `device` is a name such as `nvme0n1` rather than an absolute path.

Test signals: enumeration tests should check capacity/sector size and device naming against actual kernel devices.
