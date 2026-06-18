# sources/distributed-fs/ceph-client/drivers/input/Makefile

## Purpose

The input Makefile maps input subsystem Kconfig symbols to core objects, helper modules, userland handlers, tests, and hardware driver subdirectories.

## Important APIs, Types, and Functions

`obj-$(CONFIG_INPUT) += input-core.o` builds the composite core from `input.o`, `input-compat.o`, `input-mt.o`, `input-poller.o`, `ff-core.o`, `touchscreen.o`, and `touch-overlay.o`. Other rules build `ff-memless.o`, sparse/matrix/vivaldi keymap helpers, LED/mouse/joystick/event handlers, input tests, `apm-power.o`, RMI4 core, and hardware subdirectories.

## Control Flow

There is no runtime flow. Kbuild expands enabled symbols into objects and subdirectories. Built-in symbols link into the kernel image, while modular symbols produce modules where allowed by the surrounding Kconfig.

## State and Persistence Behavior

The Makefile affects build artifacts only. The composite object list determines which core input features are always present when `CONFIG_INPUT` is enabled.

## Dependencies and Integration Points

It consumes symbols from `drivers/input/Kconfig` and hardware-family Kconfig files. It is the build bridge from top-level input configuration to subdirectories such as `keyboard/`, `mouse/`, `touchscreen/`, `misc/`, `serio/`, and `gameport/`.

## Risks and Edge Cases

Adding a source file without updating the composite list or symbol rule silently omits code. Renaming objects without updating rules breaks builds. Subdirectory rules depend on matching Kconfig symbols such as `CONFIG_INPUT_KEYBOARD` and `CONFIG_RMI4_CORE`.

## Test Signals

Useful checks include `make M=drivers/input`, full builds with `CONFIG_INPUT=y` and `=m`, modular builds for handlers/helpers, KUnit input test builds, `CONFIG_INPUT_APMPOWER=m`, and hardware subdirectory selection.
