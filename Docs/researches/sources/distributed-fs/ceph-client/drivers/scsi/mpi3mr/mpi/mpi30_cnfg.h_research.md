# sources/distributed-fs/ceph-client/drivers/scsi/mpi3mr/mpi/mpi30_cnfg.h

## Purpose
`mpi30_cnfg.h` defines the MPI 3.0 configuration-page wire ABI used by the Broadcom `mpi3mr` driver and controller firmware. It provides config request and page header structures, page type/action/address constants, common SAS/PCIe link encodings, manufacturing pages, IO unit pages, IOC pages, driver policy pages, security pages, SAS topology pages, PCIe topology pages, enclosure pages, and device pages.

## Important APIs, Types, And Functions
The top-level request/response contract is `struct mpi3_config_request`, which carries a host tag, MPI function, change count, proxy IOC number, page version/number/type, action, page address, page length, and one SGE for the page buffer. `struct mpi3_config_page_header` prefixes each config page with version, number, attribute, length, and type.

Config selectors include `MPI3_CONFIG_PAGETYPE_*`, `MPI3_CONFIG_PAGEATTR_*`, and `MPI3_CONFIG_ACTION_*`. Page-address forms cover device handles, SAS expander handle/phy combinations, SAS phy numbers, SAS ports, enclosure handles, PCIe switch handles/ports, PCIe links, security slots, and generic instances.

Manufacturing pages `mpi3_man_page0` through `mpi3_man_page21` and `mpi3_man_page_product_specific` describe board identity, VPD, tracer data, WWIDs, GPIOs, receptacles, phy-to-slot maps, resource limits, ISTWI controllers/devices, SGPIO LED patterns, slot-status translation, certificate/SPDM/hash capabilities, licensed personalities, and OEM policies.

IO unit pages `mpi3_io_unit_page0` through `mpi3_io_unit_page19` describe NVDATA versions, write-cache and device-missing-delay policy, GPIO values, thermal thresholds/current temperatures, spin-up groups, power requirements, secure boot/current key digests, first-device ordering, firmware/silicon identifiers, profile limits, interrupt coalescing buckets, function/page access restrictions, power budgeting, current keys, direct-attached temperature polling, and per-device temperatures.

IOC pages `mpi3_ioc_page0` through `mpi3_ioc_page2` expose PCI identity, interrupt coalescing, and event masks. Driver pages `mpi3_driver_page0`, `mpi3_driver_page1`, `mpi3_driver_page2`, `mpi3_driver_page10`, `mpi3_driver_page20`, and `mpi3_driver_page30` define BIOS/driver policy, diagnostic buffer sizing, diagnostic triggers, and allowed SCSI/ATA/NVMe command lists.

Security pages define MAC/nonce/root digest/certificate/key storage through `mpi3_security_page0`, `mpi3_security_page1`, `mpi3_security_page2`, `mpi3_security_page3`, `mpi3_security_page10`, `mpi3_security_page11`, and `mpi3_security_page12`. SAS pages describe IO unit phys, expander pages, ports, phys, phy counters/events, event configuration, and initial frames. PCIe pages describe IO unit links, switch pages, link counters, ASPM, clock/reset override, and recovery actions. Device pages `mpi3_device_page0` and `mpi3_device_page1` describe SAS/SATA, PCIe/NVMe, and virtual-drive device identities and counters through form-specific unions.

## Control Flow
This header has no executable control flow. Runtime config flow in the driver builds `mpi3_config_request`, selects an action such as page-header read, current read, persistent read, current write, or persistent write, fills page address fields with the corresponding `*_PGAD_*` form, DMA maps a page buffer described by the SGE, and interprets the returned page by casting it to the matching struct and checking its page-version and bitfields.

The struct layout determines how the driver enumerates topology: get-next-handle forms walk device, enclosure, SAS expander, PCIe switch, and link pages; per-phy/per-port address forms select detailed SAS or PCIe link pages; driver and IO unit pages configure policy; security pages select certificate/key slots; and device page unions are decoded according to `device_form`.

## State And Persistence
The header describes firmware/controller state rather than local kernel state. Config actions distinguish defaults, current volatile settings, and persistent settings stored by the controller. Pages marked changeable or persistent can affect controller behavior beyond one request, while read-only pages expose hardware, topology, capability, and telemetry state.

Variable-length arrays use default maximum macros such as `MPI3_MAN*_MAX`, `MPI3_IOUNIT*_MAX`, `MPI3_SAS_*_MAX`, and `MPI3_PCIE_*_MAX`, often defaulting to 1 unless overridden before inclusion. Runtime page lengths in the header must be used to size buffers correctly when the firmware reports more entries than the compile-time default shape.

## Dependencies And Integration Points
The header depends on Linux fixed-width little-endian types (`__le16`, `__le32`, `__le64`) and MPI common definitions such as `union mpi3_sge_union` and `union mpi3_version_union` from other MPI headers included by the driver. It integrates with `mpi3mr` firmware-management code, topology discovery, SAS transport exposure, PCIe/NVMe device handling, enclosure/slot management, diagnostics, security/certificate management, and application or ioctl paths that expose controller configuration.

## Risks And Edge Cases
This is a firmware ABI surface: field ordering, endian annotations, lengths, and numeric constants must match the controller specification exactly. Any local refactor that changes struct layout or maximum-array assumptions can corrupt DMA buffers or misinterpret firmware data.

Many pages contain flexible arrays or compile-time placeholder maxima. Code must trust returned page lengths and allocate enough memory before reading full pages; using `sizeof(struct page)` with a default max of 1 can silently truncate multi-entry pages. Conversely, unvalidated firmware counts can lead to out-of-bounds parsing if consumers ignore allocated length.

Persistent-write actions can alter controller NVDATA, device exposure, security keys, access policy, power behavior, or topology configuration. Driver code must separate read-only discovery from current/persistent mutation and should gate security and policy writes carefully.

Several fields are masks and shifts over packed values for access status, link rates, ASPM, RAID state, PI capability, recovery reasons, and command blocking. Misapplying masks across SAS, PCIe, and virtual-device forms can expose the wrong queue depth, block devices incorrectly, or mishandle degraded/hidden/unauthorized devices.

## Test Signals
Build tests should validate all structs under endian type checking and all consuming code after MPI header updates. ABI tests should compare key struct sizes, offsets, page numbers, page versions, and constants against vendor specification or firmware traces. Runtime tests should read page headers and full pages for manufacturing, IO unit, IOC, driver, SAS, PCIe, enclosure, and device pages; enumerate get-next handles; parse variable-length arrays; validate persistent/current/default action separation; exercise event-mask and coalescing settings; and verify SAS transport and PCIe/NVMe device attributes derived from these pages.
