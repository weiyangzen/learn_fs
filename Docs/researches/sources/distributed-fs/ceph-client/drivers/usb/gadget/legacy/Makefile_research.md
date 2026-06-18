# sources/distributed-fs/ceph-client/drivers/usb/gadget/legacy/Makefile

## Purpose

`legacy/Makefile` maps legacy USB gadget Kconfig symbols to module objects and sets include paths needed by precomposed gadget sources.

## Important APIs, Types, and Functions

The file defines `ccflags-y` include paths for gadget core, UDC, and function headers. It maps module objects such as `g_zero-y := zero.o`, `g_audio-y := audio.o`, `g_ether-y := ether.o`, `g_hid-y := hid.o`, `g_dbgp-y := dbgp.o`, and `g_acm_ms-y := acm_ms.o`. It then uses `obj-$(CONFIG_...) += ...` to include each object in the build.

## Control Flow

Kbuild expands the selected `obj-*` entries based on `.config`, compiles the corresponding source file, and links built-in or module objects according to tristate values. Composite object names determine resulting module names such as `g_audio`, `g_ether`, `g_hid`, and `g_acm_ms`.

## State and Persistence Behavior

There is no runtime state. The Makefile affects build artifacts only.

## Dependencies and Integration Points

It integrates Kconfig selections with Kbuild and depends on headers in sibling gadget core/function/UDC directories. Source files rely on those include paths for `u_*` option headers and libcomposite declarations.

## Risks and Test Signals

Risks include stale object mappings, missing new legacy gadget entries, or module name mismatches with Kconfig help and userspace expectations. Test signals are clean builds for each `CONFIG_USB_*` selection and module-install output matching expected names.
