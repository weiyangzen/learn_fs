<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/qemu_fw_cfg.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/qemu_fw_cfg.h

Purpose: defines the userspace ABI and selector constants for QEMU firmware configuration entries exposed by the fw_cfg device.

Important APIs and types: constants identify fw_cfg signature, ID, UUID, RAM size, boot devices, kernel/initrd/cmdline/setup entries, file directory, write channel, architecture-local selector range, invalid selector, register width, file-name length, signature length, DMA feature bits, DMA control bits, and vmcoreinfo format values. `struct fw_cfg_file` describes directory entries with size, selector, reserved field, and name. `struct fw_cfg_dma_access` describes DMA control, length, and guest physical address. `struct fw_cfg_vmcoreinfo` describes host/guest vmcoreinfo format, size, and physical address.

Control flow: guest firmware, kernel drivers, or userspace select fw_cfg entries and read values or file directory contents; DMA-capable paths submit a `fw_cfg_dma_access` descriptor to QEMU.

State and persistence: fw_cfg data is supplied by the virtual machine monitor for the guest boot/runtime. It is not guest-persistent unless backed by QEMU configuration.

Dependencies and integration points: depends on Linux fixed and endian types. Integrates with QEMU virtual hardware, firmware/bootloaders, ACPI/SMBIOS/initrd passing, vmcoreinfo/crash dump plumbing, and guest userspace tools reading `/sys/firmware/qemu_fw_cfg`.

Risks and test signals: risks include endian handling, selector/address width mistakes, DMA control ordering, and trusting host-provided data. Test fw_cfg file directory reads, DMA vs non-DMA paths, invalid selectors, and QEMU machine/version compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/qemu_fw_cfg.h -->
