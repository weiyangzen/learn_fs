<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mod_devicetable.h -->
# sources/distributed-fs/ceph-client/include/linux/mod_devicetable.h

## Purpose
`mod_devicetable.h` defines the device-ID table records exported by modules and parsed by `scripts/mod/file2alias.c` to generate modaliases for userspace autoloading. It is a cross-subsystem ABI header and must stay synchronized with alias generation logic.

## Important APIs, Types, and Functions
The header defines `kernel_ulong_t`, `PCI_ANY_ID`, bus-specific match flags, modalias prefixes, and a large set of ID structs: `pci_device_id`, `ieee1394_device_id`, `usb_device_id`, `hid_device_id`, `ccw_device_id`, `ap_device_id`, `css_device_id`, `acpi_device_id`, `pnp_device_id`, `pnp_card_device_id`, `serio_device_id`, `hda_device_id`, `sdw_device_id`, `of_device_id`, `vio_device_id`, `pcmcia_device_id`, `input_device_id`, `eisa_device_id`, `parisc_device_id`, `sdio_device_id`, `ssb_device_id`, `bcma_device_id`, `virtio_device_id`, `hv_vmbus_device_id`, `rpmsg_device_id`, `i2c_device_id`, `pci_epf_device_id`, `i3c_device_id`, `spi_device_id`, `slim_device_id`, `apr_device_id`, `spmi_device_id`, `dmi_system_id`, `platform_device_id`, `mdio_device_id`, `zorro_device_id`, `isapnp_device_id`, `amba_id`, `mips_cdmm_device_id`, `x86_cpu_id`, `cpu_feature`, `ipack_device_id`, `mei_cl_device_id`, `rio_device_id`, `mcb_device_id`, `ulpi_device_id`, `fsl_mc_device_id`, `tb_service_id`, `typec_device_id`, `tee_client_device_id`, `wmi_device_id`, `mhi_device_id`, `auxiliary_device_id`, `ssam_device_id`, `dfl_device_id`, `ishtp_device_id`, `cdx_device_id`, `vchiq_device_id`, and `coreboot_device_id`.

## Control Flow and State
Driver code declares static ID arrays and exports them with `MODULE_DEVICE_TABLE()`. During build, `file2alias.c` reads these structures from module ELF metadata and emits modalias patterns. At runtime, bus cores compare device attributes against these tables and pass matched entries to probe callbacks.

## State and Persistence Behavior
The tables are static read-only module data and may also become userspace-visible module alias metadata. `driver_data`/`driver_info` fields persist for the lifetime of the driver table and often encode quirk flags or indices.

## Dependencies and Integration Points
The header is tightly coupled to bus cores, module metadata generation, kmod autoloading, `file2alias.c`, uevent/modalias strings, and userspace tools such as udev/modprobe. Some structures use `uuid_t`, `guid_t`, MEI, PCI, USB, ACPI, OF, DMI, and network PHY conventions.

## Risks
Any layout, name, size, or field-order change can break module alias generation or userspace ABI. Pointer-sized `kernel_ulong_t` makes cross-architecture output sensitive. Match flags must align with bus matching code. Tables often require zero terminators; missing terminators can overrun matching loops.

## Test Signals
Build `modpost`, inspect generated `modules.alias`, run hotplug/autoload tests across representative buses, verify 32-bit and 64-bit module builds, and compile drivers using each table macro.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mod_devicetable.h -->
