# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hnae3.h

## Purpose

`hnae3.h` is the central interface contract for the Hisilicon HNS3 Ethernet acceleration engine framework. It defines PCI device identifiers, firmware/device capability bits, reset and debug command enums, queue and ring abstractions, device specification structures, client registration structures, the large `hnae3_ae_ops` operations vector implemented by PF/VF hardware backends, DCB callbacks, and per-client private state for KNIC and RoCE consumers.

## Important APIs, Types, and Macros

- Capability helpers such as `hnae3_dev_roce_supported()`, `hnae3_dev_fec_supported()`, `hnae3_ae_dev_cq_supported()`, and related `test_bit()` wrappers expose firmware capability state from `struct hnae3_ae_dev::caps`.
- Ring helpers `ring_ptr_move_fw()` and `ring_ptr_move_bw()` wrap ring indices by `desc_num`.
- `struct hnae3_queue` models a TQP queue with MMIO bases, owner handle, queue index, buffer size, and TX/RX descriptor counts.
- `struct hnae3_dev_specs` stores firmware-discovered hardware limits such as RSS table/key sizes, interrupt moderation maxima, MAC table sizes, frame size, TQP/qset counts, tunnel count, and Hilink version.
- `struct hnae3_client`, `struct hnae3_client_ops`, `struct hnae3_ae_dev`, and `struct hnae3_ae_algo` define the client/backend registration layer.
- `struct hnae3_ae_ops` is the primary backend vtable for lifecycle, link, MAC, VLAN, RSS, coalescing, stats, register dumps, vectors, reset, SR-IOV, flow director, PTP, WOL, debugfs, and hardware timestamp operations.
- `struct hnae3_dcb_ops` defines IEEE ETS/PFC/application and DCBX operations consumed by `hns3_dcbnl.c`.
- `struct hnae3_knic_private_info` stores netdev-facing state: RSS sizes, descriptor counts, TC mapping, DSCP priority mapping, TQPs, DCB ops, and MMIO base.
- `struct hnae3_roce_private_info` stores RoCE netdev, MMIO bases, vector assignment, and state bitmaps.
- `hnae3_set_field()`, `hnae3_get_field()`, `hnae3_set_bit()`, and `hnae3_get_bit()` are shared bitfield helpers used by command/RSS code.
- `hnae3_format_mac_addr()` masks middle MAC octets for safer formatted display.
- Public registration functions include `hnae3_register_ae_dev()`, `hnae3_unregister_ae_dev()`, `hnae3_register_ae_algo()`, `hnae3_unregister_ae_algo()`, `hnae3_register_client()`, and `hnae3_unregister_client()`.

## Control Flow and Integration

The header does not execute control flow itself except for inline helpers. Its definitions shape the runtime flow across the driver: PCI PF/VF code registers an `hnae3_ae_algo`, creates an `hnae3_ae_dev`, binds clients through `hnae3_client_ops`, and exposes hardware behavior through `hnae3_ae_ops`. Netdev, ethtool, debugfs, DCBNL, RSS, stats, reset, and RoCE paths all dereference these vtables through `struct hnae3_handle`. Debugfs helpers use `hnae3_seq_file_to_ae_dev()` and `hnae3_seq_file_to_handle()` to recover driver objects from seq files.

## State and Persistence Behavior

All persistent driver state described here is in memory and tied to the PCI device lifetime. Capability bits in `hnae3_ae_dev::caps`, feature flags in `hnae3_ae_dev::flag`, private flags in `hnae3_handle`, TQP arrays, TC/DSCP maps, and debugfs dentries persist until device removal, reset teardown, or client unregistration. No on-disk state is defined. Several structures reflect firmware state cached in the driver, so reset and reinitialization paths must refresh or preserve them deliberately.

## Dependencies

The header depends on Linux networking, PCI, DCBNL, ethtool, ACPI, bitmap, packet scheduler, and traffic control headers. It is consumed by HNS3 PF/VF backend files, common command/RSS/stats modules, NIC frontend code, debugfs, and DCBNL wrappers.

## Risks and Edge Cases

- `struct hnae3_ae_ops` is broad and mostly optional by convention; callers must check function pointers before invoking optional operations.
- Capability helper correctness depends on firmware capability parsing and the bit mapping in command code.
- `hnae3_set_field()` and `hnae3_set_bit()` evaluate the `origin` lvalue multiple times and assume masks/shifts are valid.
- `ring_ptr_move_bw()` assumes `desc_num` is nonzero.
- `hnae3_seq_file_to_handle()` assumes seq file private data carries an `hnae3_ae_dev` with a live handle.
- `struct hnae3_handle` uses a union where `netdev` must remain the first member for netdev-oriented access.

## Test Signals

Useful validation signals include successful PF/VF probe and removal, client registration/unregistration, ethtool operations routed through `hnae3_ae_ops`, DCB setup only when supported, reset notification coverage, debugfs reads resolving the correct handle, RSS/TC configuration bounded by `hnae3_dev_specs`, and capability-dependent features enabling only when the relevant bit is set.
