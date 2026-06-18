# sources/distributed-fs/ceph-client/drivers/scsi/isci/Makefile

## Purpose

This Makefile declares the Intel C600/Xeon E3 SAS controller low-level driver object composition. It builds the `isci` module when `CONFIG_SCSI_ISCI` is enabled and lists every translation unit linked into the composite `isci.o` object.

## Important APIs, Types, and Functions

The key build declarations are `obj-$(CONFIG_SCSI_ISCI) += isci.o` and `isci-objs := ...`. The object list includes `init.o`, `phy.o`, `request.o`, `remote_device.o`, `port.o`, `host.o`, `task.o`, `probe_roms.o`, `remote_node_context.o`, `remote_node_table.o`, `unsolicited_frame_control.o`, and `port_config.o`.

## Control Flow

There is no runtime control flow in the file, but the object order defines what source files participate in the module link. `init.o` supplies module and PCI entry points; `host.o` supplies controller lifecycle, interrupts, DMA setup, and request posting; `phy.o` supplies phy state handling; the remaining files supply ports, devices, requests, task management, firmware/OEM parameter parsing, remote-node allocation, unsolicited-frame handling, and port configuration.

## State and Persistence Behavior

The Makefile stores no runtime state. Its persistent effect is build-system state: enabling or disabling `CONFIG_SCSI_ISCI` determines whether the driver is present in the kernel or module build.

## Dependencies and Integration Points

It integrates with kbuild's composite-object convention. The file assumes all listed objects are in the same directory and that `CONFIG_SCSI_ISCI` is provided by the SCSI Kconfig tree. The module source set also implicitly depends on libsas, PCI, DMA, firmware loading, and SCSI transport support through the linked source files.

## Risks and Edge Cases

Dropping an object from `isci-objs` can compile successfully only if no symbols from that object are referenced, but it may silently remove subsystem behavior such as ROM parsing or frame control. Adding new source files requires updating this list. The trailing backslash style means accidental whitespace or deletion at line ends can alter the object list.

## Test Signals

The primary signal is a successful kernel build with `CONFIG_SCSI_ISCI=m` or `y`, producing an `isci` module/object with all expected symbols. Runtime smoke tests should show the `isci` PCI driver registering, firmware name advertised, and libsas callbacks wired from the linked units.
