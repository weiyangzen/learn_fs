# sources/distributed-fs/ceph-client/drivers/acpi/bgrt.c

## Purpose
Publishes the ACPI Boot Graphics Resource Table (BGRT) through sysfs. It lets userspace inspect firmware-provided boot-logo metadata and read the boot image bytes under the firmware ACPI kobject.

## Important APIs, Types, And Functions
`acpi_parse_bgrt()` is the ACPI table parser hook; it delegates to `efi_bgrt_init()` to populate the global EFI BGRT state. `bgrt_init()` is a `device_initcall` that maps the image memory and creates the sysfs group. The `BGRT_SHOW()` macro defines read-only attributes for `version`, `status`, `type`, `xoffset`, and `yoffset`. `BIN_ATTR_SIMPLE_RO(image)` exposes the mapped image as a binary sysfs attribute.

## Control Flow
Table parsing runs during ACPI table discovery and initializes `bgrt_tab` and `bgrt_image_size`. Later, `bgrt_init()` exits with `-ENODEV` if no image address exists. Otherwise it `memremap()`s the image, stores the pointer and size in `bin_attr_image`, creates `/sys/firmware/acpi/bgrt` below `acpi_kobj`, and attaches the attribute group. Errors unwind the kobject and memory mapping.

## State And Persistence
The only persistent runtime state is `bgrt_image`, `bgrt_kobj`, and the global BGRT metadata from EFI helpers. The mapped image remains available for the lifetime of the sysfs object; there is no explicit module exit path because this is built as core firmware support.

## Dependencies And Integration Points
Depends on `linux/efi-bgrt.h`, sysfs kobjects, `memremap()`, and the ACPI firmware kobject exported by `bus.c`. Userspace consumes the metadata and binary image under `/sys/firmware/acpi/bgrt`.

## Risks
Incorrect firmware image addresses or sizes can make `memremap()` fail or expose invalid data. The file assumes `acpi_kobj` exists by device init time. Since the binary attribute directly exposes firmware memory contents, bounds correctness in `bgrt_image_size` is important.

## Test Signals
Presence of `/sys/firmware/acpi/bgrt/{version,status,type,xoffset,yoffset,image}` on BGRT-capable EFI systems, successful image reads of exactly `bgrt_image_size`, and clean absence on systems with no BGRT are the main signals. Error-path testing should force mapping or sysfs creation failure.
