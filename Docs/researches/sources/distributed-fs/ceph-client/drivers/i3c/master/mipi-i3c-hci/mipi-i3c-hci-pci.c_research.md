# sources/distributed-fs/ceph-client/drivers/i3c/master/mipi-i3c-hci/mipi-i3c-hci-pci.c

## Purpose

`mipi-i3c-hci-pci.c` is PCI glue for Intel LPSS MIPI I3C HCI controllers. It maps the PCI BAR, performs Intel-specific reset/LTR/debugfs setup, creates one or two platform/MFD child instances of the generic `mipi-i3c-hci` driver, and coordinates parent-managed runtime/system PM for those children.

## Important APIs, Types, and Functions

- `struct mipi_i3c_hci_pci` stores the PCI device, shared base mapping, instance metadata, per-instance operational flags, and vendor private data.
- `struct mipi_i3c_hci_pci_info` describes SoC-specific child instance offsets, IDs, name, count, and PM ownership.
- Intel private registers cover reset and active/idle LTR programming.
- `intel_i3c_init()` sets a 64-bit DMA mask, removes D3 delays, resets the Intel host block, exposes PM QoS latency tolerance, and creates debugfs LTR files.
- `mipi_i3c_hci_pci_add_instances()` builds `mfd_cell` entries with platform data pointing at per-instance base offsets and a shared IRQ.
- Parent PM callbacks call exported `i3c_hci_rpm_suspend()`/`i3c_hci_rpm_resume()` on operational child platform devices.
- The PCI ID table covers Wildcat Lake, Panther Lake, and Nova Lake variants with one or two instances.

## Control Flow

Probe enables the PCI device, sets bus mastering, maps BAR 0, allocates one IRQ vector, selects the `pci_info` from `driver_data`, runs vendor init, adds MFD children, stores driver data, and allows runtime PM. Each child platform device receives `mipi_i3c_hci_platform_data.base_regs` pointing into the shared BAR at the configured instance offset. Remove calls vendor exit, forbids runtime PM, and removes MFD children.

For PM, the parent walks child devices. Suspend iterates in reverse and records children whose HCI bus was operational before calling child RPM suspend. If one suspend fails, previously suspended children are resumed. Resume walks forward and resumes only children recorded as operational, with rollback on failure.

## State and Persistence Behavior

Intel LTR register values are cached in `struct intel_host` and exposed read-only in debugfs. Per-child `operational` flags remember whether the child bus was enabled before parent suspend. Platform data references the shared BAR mapping and remains valid for child lifetime.

## Dependencies and Integration Points

This file integrates PCI, MFD, platform data, debugfs, PM QoS, runtime PM, and the generic HCI platform driver. It depends on `core.c` exporting RPM helpers and on the generic HCI platform driver matching child name `intel-lpss-i3c`.

## Risks and Edge Cases

`mipi_i3c_hci_pci_find_instance()` assigns the first empty instance slot while checking PM state; unexpected child ordering or more than `INST_MAX` children would fail. Parent-managed PM assumes children with disabled bus do not need RPM suspend/resume. Intel reset ignores the poll return value. Cell platform data is passed to `mfd_add_devices()` from scoped allocations, relying on MFD copying `platform_data` by `pdata_size`.

## Test Signals

Test PCI probe/remove, child count/offset/ID per PCI ID, shared IRQ delivery, DMA mask selection with IOMMU, debugfs LTR values, PM QoS writes changing LTR registers, parent suspend/resume rollback, and child HCI transfers after resume.
