# sources/distributed-fs/ceph-client/drivers/most/Makefile

## Purpose
This Makefile wires the MOST subsystem Kconfig symbols to kernel build targets.

## Important build rules
- `obj-$(CONFIG_MOST) += most_core.o` builds the core when `MOST` is enabled.
- `most_core-y := core.o configfs.o` links `core.c` and `configfs.c` into the core module/object.
- `obj-$(CONFIG_MOST_USB_HDM) += most_usb.o` builds the USB hardware-dependent module.
- `obj-$(CONFIG_MOST_CDEV) += most_cdev.o` builds the cdev userspace component.
- `obj-$(CONFIG_MOST_SND) += most_snd.o` builds the sound component.

## Control flow and integration behavior
There is no runtime control flow. Build flow is controlled by Kbuild expansion of `obj-*` and composite object rules. Because `configfs.o` is part of `most_core-y`, configfs support is compiled into the core object rather than as a separate module.

## State and persistence
The file has no runtime state. Its effects are build artifacts determined by kernel configuration.

## Dependencies and integration points
This Makefile integrates with the Kbuild system and the symbols defined by the adjacent Kconfig. The source files referenced here provide the core bus/buffer manager, configfs interface, USB HDM, character device component, and sound component.

## Risks and edge cases
- Renaming source files or Kconfig symbols without updating this Makefile breaks builds.
- `most_core-y` means `configfs.c` initialization is expected from core initialization; any change to that coupling must adjust both files.
- Component modules depend at runtime on symbols exported from the core, so build configurations should ensure module dependencies are generated.

## Test signals
Useful checks are `make M=drivers/most` for all enabled combinations, module dependency inspection for `most_cdev` and `most_sound`, and confirming `most_core.o` contains both core and configfs objects.
