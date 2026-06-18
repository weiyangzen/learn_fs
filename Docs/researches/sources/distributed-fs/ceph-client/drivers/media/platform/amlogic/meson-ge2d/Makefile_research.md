
# sources/distributed-fs/ceph-client/drivers/media/platform/amlogic/meson-ge2d/Makefile

## Purpose

This Makefile maps `CONFIG_VIDEO_MESON_GE2D` to the GE2D driver object. It builds the single-source V4L2 mem2mem accelerator driver.

## Important APIs, Types, And Functions

There are no runtime APIs. The only Kbuild directive is `obj-$(CONFIG_VIDEO_MESON_GE2D) += ge2d.o`.

## Control Flow

Kbuild includes `ge2d.o` in the built-in image, module build, or neither according to the Kconfig symbol value.

## State And Persistence

The file has no runtime state. Build artifacts are the only output.

## Dependencies And Integration Points

It integrates with the GE2D Kconfig and parent media platform build. It assumes the whole driver implementation is in `ge2d.c`.

## Risks

Low risk for the current single-file driver. Any future split into register helpers, format tables, or platform variants must update the object list.

## Test Signals

Compile with `CONFIG_VIDEO_MESON_GE2D=m` and confirm `ge2d.o` and a loadable module are generated. Compile with the symbol disabled and confirm the object is not built.
