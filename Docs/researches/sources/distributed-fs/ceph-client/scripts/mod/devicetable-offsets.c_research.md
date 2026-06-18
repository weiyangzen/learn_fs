<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/mod/devicetable-offsets.c -->
# sources/distributed-fs/ceph-client/scripts/mod/devicetable-offsets.c

## Purpose

`devicetable-offsets.c` emits C-structure sizes and field offsets for all `struct *_device_id` tables consumed by `file2alias.c`. It lets a host tool decode target-built module data without assuming host ABI layout.

## Important APIs, Types, and Functions

Macros `DEVID()` and `DEVID_FIELD()` wrap `DEFINE()` from `linux/kbuild.h`. `main()` enumerates each supported device-id type and the fields needed to build module alias strings.

## Control Flow

Kbuild compiles the file to assembly, where `DEFINE()` markers are then extracted by `filechk offsets` into `devicetable-offsets.h`. There is no runtime behavior beyond returning from `main()`.

## State and Persistence Behavior

The generated header persists size and offset constants such as `SIZE_usb_device_id` and `OFF_usb_device_id_idVendor`.

## Dependencies and Integration Points

It depends on `linux/mod_devicetable.h` and the generated-offset mechanism. It must stay in lockstep with `file2alias.c` and any kernel structures referenced by `MODULE_DEVICE_TABLE()`.

## Risks and Edge Cases

Missing a field causes aliases to be incomplete or decoded at the wrong offset. Adding a new device table requires a size entry here and a handler in `file2alias.c`. Cross-endian and packed layout issues are only safe if offsets match target compilation.

## Test Signals

Regenerate offsets after changing `mod_devicetable.h`, build modules for multiple architectures, and compare produced `MODULE_ALIAS()` strings for USB, PCI, OF, ACPI, and newer bus tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/mod/devicetable-offsets.c -->
