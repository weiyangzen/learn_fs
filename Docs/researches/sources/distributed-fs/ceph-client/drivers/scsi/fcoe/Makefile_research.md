<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/fcoe/Makefile -->
# sources/distributed-fs/ceph-client/drivers/scsi/fcoe/Makefile

## Purpose

`drivers/scsi/fcoe/Makefile` defines the kbuild object composition for the FCoE driver directory. It selects the standalone FCoE initiator object and the shared libfcoe object based on kernel configuration symbols.

## Important APIs, Types, and Functions

There are no C APIs or runtime functions. The build rules are the important interface:

- `obj-$(CONFIG_FCOE) += fcoe.o` builds the FCoE driver object when `CONFIG_FCOE` is enabled.
- `obj-$(CONFIG_LIBFCOE) += libfcoe.o` builds the shared FCoE library object when `CONFIG_LIBFCOE` is enabled.
- `libfcoe-objs := fcoe_ctlr.o fcoe_transport.o fcoe_sysfs.o` links the library from controller, transport, and sysfs support objects.

## Control Flow

Kbuild evaluates the `obj-*` variables during the kernel build. If the relevant config symbol is `y`, the object is built into vmlinux; if `m`, it is built as a module; if unset, it is omitted. `libfcoe.o` is not a source file, but a composite object linked from the three listed component objects.

## State and Persistence Behavior

The file has no runtime state and no persistence behavior. It controls which compiled objects exist and therefore which runtime FCoE code can be loaded or built in.

## Dependencies and Integration Points

The Makefile integrates with the SCSI/FCoE Kconfig symbols and kernel kbuild. `fcoe.o` depends on the source file that implements the FCoE initiator driver. `libfcoe.o` groups common library functionality used by FCoE code, including controller logic, transport glue, and sysfs exposure.

## Risks and Edge Cases

Build failures can occur if Kconfig allows `CONFIG_FCOE` without the necessary library dependencies or if source object names drift from the Makefile. Because `libfcoe.o` is composite, missing one component can remove controller, transport, or sysfs functionality from every user of the library. Module/built-in combinations must satisfy symbol visibility between `fcoe.o` and `libfcoe.o`.

## Test Signals

Validation is kbuild-oriented: build with FCoE disabled, with `CONFIG_LIBFCOE=m`, with `CONFIG_FCOE=m`, and with built-in variants; verify `libfcoe.o` contains `fcoe_ctlr.o`, `fcoe_transport.o`, and `fcoe_sysfs.o`; run `modpost` for unresolved symbols; and confirm the expected modules or built-in objects appear in the build output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/fcoe/Makefile -->
