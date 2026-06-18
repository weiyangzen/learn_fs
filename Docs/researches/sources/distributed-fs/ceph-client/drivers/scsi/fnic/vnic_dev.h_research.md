# sources/distributed-fs/ceph-client/drivers/scsi/fnic/vnic_dev.h

## Purpose

`vnic_dev.h` declares the vNIC device-control interface and shared descriptor-ring structure used by FNIC queue, interrupt, and firmware-command code.

## Important APIs, types, and data

- The top block aliases generic `vnic_dev_*` names to `fnic_dev_*` names to avoid built-in symbol clashes with Cisco ENIC.
- `readq()`/`writeq()` fallbacks implement 64-bit MMIO accesses when the architecture does not provide them.
- `enum vnic_dev_intr_mode` records INTx, MSI, or MSI-X mode.
- `struct vnic_dev_bar` describes mapped PCI BAR state.
- `struct vnic_dev_ring` records coherent descriptor memory, aligned base address, descriptor size/count, and software availability.
- Prototypes cover resource lookup, ring allocation, firmware commands, stats, notification, link helpers, open/close/reset, interrupt mode, and registration.

## Control flow

The header is consumed by queue helpers and the FNIC driver. Probe code registers a device with a BAR, initializes command support, allocates rings through the declared helpers, and later uses command wrappers for device lifecycle and state.

## State and persistence behavior

No state is allocated in the header. The key persistent state described here is `struct vnic_dev_ring`, whose `desc_avail` field is maintained by queue helpers while the DMA memory remains shared with hardware.

## Dependencies and integration points

It depends on `vnic_resource.h` and `vnic_devcmd.h`, kernel DMA/MMIO types, and PCI device structures. It is included by all FNIC vNIC queue/control modules.

## Risks and edge cases

- The alias `#define vnic_dev_desc_ring_size fnic_dev_desc_ring_siz` appears truncated; it must match object naming expectations at compile/link time.
- The fallback `writeq()` writes low then high 32-bit halves; hardware must tolerate that ordering.
- Consumers must maintain ring availability consistently or hardware/software ownership breaks.

## Test signals

Compile coverage with FNIC and ENIC built-in together is important for alias correctness. Runtime ring allocation tests should validate alignment and descriptor counts.
