# sources/distributed-fs/ceph-client/drivers/hid/Makefile

## Purpose

This Makefile maps HID Kconfig symbols to core HID objects, vendor-specific drivers, test objects, and transport subdirectories. It is the build-time companion to `drivers/hid/Kconfig`.

## Important APIs, Types, and Functions

The primary build targets are `hid.o`, assembled from `hid-core.o`, `hid-input.o`, and `hid-quirks.o`, with optional `hid-debug.o`, `hid-haptic.o`, and `hidraw.o`. `obj-$(CONFIG_HID_BPF) += bpf/` enters the HID-BPF subdirectory. `obj-$(CONFIG_AMD_SFH_HID) += amd-sfh-hid/` enters the AMD SFH transport. Composite targets include `hid-logitech-y`, `hid-wiimote-y`, `hid-picolcd-y`, `hid-uclogic-objs`, `wacom-objs`, and `hid-uclogic-test-objs`.

## Control Flow

Kbuild evaluates each `obj-$(CONFIG_...)` line after Kconfig resolves symbols. Enabled built-in symbols add objects to vmlinux; module symbols build modules. Composite object lists are resolved first, then the corresponding `obj-*` line decides whether the composite target is linked.

## State and Persistence Behavior

The Makefile has no runtime state. Its persistent effect is the kernel image or module set produced by the selected configuration. Composite objects also define linkage boundaries, for example Wacom code is linked as `wacom.o` from `wacom_wac.o` and `wacom_sys.o`.

## Dependencies and Integration Points

It integrates directly with Kconfig symbols in `drivers/hid/Kconfig` and subdirectory Kconfigs. It also routes bus transports to `usbhid/`, `i2c-hid/`, `intel-ish-hid/`, `amd-sfh-hid/`, `surface-hid/`, and `intel-thc-hid/`.

## Risks and Test Signals

Risks are symbol/object mismatches, duplicate object inclusion, and composite object lists that omit a needed source file. Test signals include Kbuild with `CONFIG_HID=y/m`, `CONFIG_HID_BPF=y/m`, `CONFIG_AMD_SFH_HID=y/m`, and randconfig builds that stress optional composites such as force feedback and KUnit.
