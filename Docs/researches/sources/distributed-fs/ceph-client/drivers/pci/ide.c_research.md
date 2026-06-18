# sources/distributed-fs/ceph-client/drivers/pci/ide.c

## Purpose
Implements PCIe Integrity and Data Encryption (IDE) stream discovery, allocation, registration, register programming, enable/disable, teardown, and host-bridge stream accounting.

## Important APIs, Types, and Functions
Public APIs include `pci_ide_init()`, `pci_ide_stream_alloc()`, `pci_ide_stream_free()`, `pci_ide_stream_release()`, `pci_ide_stream_register()`, `pci_ide_stream_unregister()`, `pci_ide_to_settings()`, `pci_ide_stream_setup()`, `pci_ide_stream_teardown()`, `pci_ide_stream_enable()`, `pci_ide_stream_disable()`, `pci_ide_init_host_bridge()`, `pci_ide_set_nr_streams()`, and `pci_ide_destroy()`. Important helper types are `struct stream_index`, `struct pci_ide_stream_id`, `struct pci_ide`, `struct pci_ide_partner`, and `struct pci_ide_regs`.

## Control Flow
Device init finds the IDE extended capability, requires Selective IDE, requires endpoints to have an IDE-capable root port, discovers link/selective stream counts and address-association block counts, claims any streams already active, and programs inactive stream IDs to the reserved ID. Stream allocation reserves a host-bridge stream, root-port selective stream index, and endpoint selective stream index, computes RID ranges including enabled VFs, and records downstream memory/prefetchable windows. Registration reserves the requested stream ID and creates a host-bridge sysfs link. Setup converts RID and address associations into config register writes for endpoint or root-port partner blocks, then writes control disabled but with stream ID/config fields. Enable sets the enable bit and requires the status state to become secure.

## State and Persistence Behavior
Per-device state includes `pdev->ide_cap`, stream counts, TEE/config limits, per-device IDA for stream indexes, and hardware selective/link stream registers. Host-bridge state includes stream count and IDAs for stream resources and stream IDs. `struct pci_ide` tracks partner setup/enable flags and a sysfs link name so `pci_ide_stream_release()` can unwind in reverse setup order.

## Dependencies and Integration Points
Depends on PCIe extended capability definitions, root-port lookup, SR-IOV helpers for VF RID ranges, bridge resource windows, IDA allocators, sysfs links, PCI config space writes, and host-bridge sysfs attribute groups.

## Risks
IDE setup is asymmetric between endpoint and root port and requires both sides to be programmed consistently. The code assumes a constant number of address-association blocks across selective streams and skips the rest otherwise. Active firmware-configured stream IDs are reserved opportunistically; failure aborts IDE initialization. `pci_ide_stream_enable()` leaves cleanup of failed secure-state entry to the caller. `pci_ide_stream_free()` appears to free `hb->ide_stream_ida` for `host_bridge_stream`, while allocation uses `hb->ide_stream_ida`; stream ID reservations separately use `ide_stream_ids_ida`.

## Test Signals
Validate IDE capability discovery on endpoints/root ports, pre-active stream reservation, host-bridge stream count override, stream alloc/register/setup/enable/disable/teardown/release, sysfs link creation/removal, SR-IOV RID range coverage, memory/prefetch window associations, secure-state failure, and cleanup under partial setup failure.
