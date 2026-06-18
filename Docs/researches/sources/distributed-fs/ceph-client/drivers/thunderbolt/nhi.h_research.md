<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thunderbolt/nhi.h -->
# sources/distributed-fs/ceph-client/drivers/thunderbolt/nhi.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/thunderbolt/nhi.h` is the local NHI contract for firmware mailbox modes/commands, optional controller-generation hooks, PCI device IDs, and the USB4 PCI class used by the NHI PCI driver. The source was read as a complete 103-line file.

## Important APIs, Types, and Functions

The header defines `enum nhi_fw_mode` (`SAFE`, `AUTH`, endpoint, and connection-manager modes), `enum nhi_mailbox_cmd` for firmware commands such as save devices, disconnect PCIe paths, driver unload, disconnect paths A/B, and allow all devices, and declares `nhi_mailbox_cmd()` and `nhi_mailbox_mode()`. `struct tb_nhi_ops` supplies optional hooks for controller-specific initialization, suspend/resume, runtime suspend/resume, and shutdown. `icl_nhi_ops` is declared as the Ice Lake and later implementation. The rest of the file is an ID catalog for Intel Thunderbolt/USB4 NHI and bridge parts through Panther/Lunar/Barlow Ridge era IDs plus `PCI_CLASS_SERIAL_USB_USB4`.

## Control Flow

This header has no executable control flow. It shapes control flow in `nhi.c` by making per-device `driver_data` point to `tb_nhi_ops`, and by defining mailbox operation values sent through NHI MMIO registers.

## State and Persistence Behavior

No storage is owned here. The enum values are protocol constants, while PCI IDs participate in module device matching for the lifetime of the driver.

## Dependencies and Integration Points

The only direct include is `<linux/thunderbolt.h>`. The header is consumed by `nhi.c`, `nhi_ops.c`, and any local code needing NHI mailbox helpers or PCI IDs. Its PCI ID constants are also referenced by quirk and switch generation logic.

## Risks and Edge Cases

Incorrect PCI IDs break device binding, quirk matching, or generation classification. Changing mailbox numeric values would send the wrong firmware commands. `tb_nhi_ops` hook semantics must stay aligned with `nhi.c` PM ordering: hooks run around domain suspend/resume and must not assume unavailable MMIO or an already resumed domain unless the caller guarantees it.

## Test Signals

Compile coverage for every user of the header, PCI modalias/module table checks, probe tests on each ID class, and PM tests for devices using `icl_nhi_ops` are the main validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thunderbolt/nhi.h -->
