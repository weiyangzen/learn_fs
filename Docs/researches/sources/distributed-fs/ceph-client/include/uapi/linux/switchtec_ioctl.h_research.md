# sources/distributed-fs/ceph-client/include/uapi/linux/switchtec_ioctl.h

## Purpose
Defines the Microsemi/Microchip Switchtec PCIe switch ioctl ABI for flash partition information, event summaries/control, and PFF-to-port mapping.

## Important APIs, Types, and Constants
Partition IDs cover config, image, NVLOG, vendor, BL2, map, and key partitions. `struct switchtec_ioctl_flash_info`, `switchtec_ioctl_flash_part_info`, `switchtec_ioctl_event_summary_legacy`, `switchtec_ioctl_event_summary`, `switchtec_ioctl_event_ctl`, and `switchtec_ioctl_pff_port` are ioctl payloads. Event IDs range through stack, PPU, ISP, firmware, MRPC, GPIO, DPC, hotplug, threshold, power, link, GFMS, intercomm, and UEC events. Event flags support clear, enable/disable polling/log/CLI/fatal. Ioctls include `SWITCHTEC_IOCTL_FLASH_INFO`, `SWITCHTEC_IOCTL_FLASH_PART_INFO`, `SWITCHTEC_IOCTL_EVENT_SUMMARY`, `SWITCHTEC_IOCTL_EVENT_SUMMARY_LEGACY`, `SWITCHTEC_IOCTL_EVENT_CTL`, `SWITCHTEC_IOCTL_PFF_TO_PORT`, and `SWITCHTEC_IOCTL_PORT_TO_PFF`.

## Control Flow, State, and Persistence
Userspace queries flash layout, maps ports, reads event bitmaps, and controls per-event behavior. Device firmware and driver maintain event counts, occurrence data, flash partitions, and PFF mappings.

## Dependencies and Integration Points
Depends on `<linux/types.h>` and ioctl encoding. Integrates with the Switchtec PCI driver and vendor management tools.

## Risks and Test Signals
Risks include legacy and current event-summary sharing the same ioctl number with different struct sizes, invalid partition indices, and accidental clearing of diagnostics. Test size-dispatch compatibility, Gen3/Gen4 partition counts, event flag validation, all-event/local-part sentinel indices, and PFF mapping round trips.
