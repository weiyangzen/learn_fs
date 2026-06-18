# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl8xxxu/Makefile

## Purpose

This Makefile wires the rtl8xxxu driver objects into the Linux kernel build. When `CONFIG_RTL8XXXU` is enabled, it builds one composite object, `rtl8xxxu.o`, from the common core and all listed chip-specific implementation files.

## Important Build Rules

- `obj-$(CONFIG_RTL8XXXU) += rtl8xxxu.o` includes the composite object when the Kconfig symbol is built-in or modular.
- `rtl8xxxu-y := core.o 8192e.o 8723b.o 8723a.o 8192c.o 8188f.o 8188e.o 8710b.o 8192f.o` defines the members of the composite driver object.
- `8723b.o` is therefore always compiled into the driver whenever `RTL8XXXU` is enabled; there is no separate chip-level Kconfig switch for RTL8723BU support.

## Control Flow and Build Behavior

Kbuild expands `obj-$(CONFIG_RTL8XXXU)` according to the selected Kconfig value:

1. `CONFIG_RTL8XXXU=n`: no object is emitted from this directory for rtl8xxxu.
2. `CONFIG_RTL8XXXU=m`: Kbuild compiles all `rtl8xxxu-y` members and links them into `rtl8xxxu.ko`.
3. `CONFIG_RTL8XXXU=y`: Kbuild compiles the same members into a built-in driver object.

Runtime chip dispatch is not controlled by this Makefile. All listed chip implementations are present in the compiled driver, and USB device matching in `core.c` chooses the appropriate `struct rtl8xxxu_fileops` table.

## State and Persistence Behavior

The Makefile has no runtime state. Its persistent effect is in build artifacts: object files, the linked module or built-in object, generated module metadata, and any module aliases derived from the compiled source.

## Dependencies and Integration Points

- Consumes `CONFIG_RTL8XXXU` from the adjacent Kconfig file.
- Integrates with Linux Kbuild composite-object semantics through the `rtl8xxxu-y` variable.
- Requires every listed object to compile and resolve symbols together. For example, `8723b.o` exports `rtl8723bu_fops`, while `core.o` references it through extern declarations and USB ID `driver_info`.
- Chip files share helper symbols from `core.o` and declarations in `rtl8xxxu.h`; ordering in `rtl8xxxu-y` does not express runtime order, only link membership.

## Risks and Edge Cases

- Adding a new chip file requires both adding its object here and connecting its fops/USB IDs in source. Updating only one side causes either missing support or unresolved/unused code.
- Removing or renaming an object listed in `rtl8xxxu-y` breaks builds whenever `RTL8XXXU` is enabled.
- Because all chip implementations are compiled together, a compile error in any chip file disables the entire rtl8xxxu driver build.
- There is no fine-grained way to reduce module size by selecting only one chip family; any such split would require Kconfig and source-level restructuring.

## Test Signals

- Build with `CONFIG_RTL8XXXU=m` and confirm `rtl8xxxu.ko` contains symbols from `core.o` and chip objects including `rtl8723bu_fops`.
- Build with `CONFIG_RTL8XXXU=y` to catch built-in link differences.
- Run `modinfo rtl8xxxu` in a module build to confirm module metadata and aliases are still generated from the compiled source.
- Use incremental build tests after modifying the object list to ensure dependencies and symbol references remain valid.
