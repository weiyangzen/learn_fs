# sources/distributed-fs/ceph-client/drivers/video/fbdev/nvidia/Makefile

## Purpose

This Makefile defines the object composition for the legacy NVIDIA fbdev driver. It builds `nvidiafb.o` when `CONFIG_FB_NVIDIA` is enabled and conditionally includes I2C and backlight support. The source was read as a complete 13-line file.

## Important APIs, Types, and Functions

The important build variables are `obj-$(CONFIG_FB_NVIDIA) += nvidiafb.o`, `nvidiafb-y`, `nvidiafb-$(CONFIG_FB_NVIDIA_I2C)`, `nvidiafb-$(CONFIG_FB_NVIDIA_BACKLIGHT)`, and `nvidiafb-objs`. The base object list is `nvidia.o nv_hw.o nv_setup.o nv_accel.o nv_of.o`; optional pieces are `nv_i2c.o` and `nv_backlight.o`.

## Control Flow

There is no runtime flow. Kbuild resolves the object list from configuration symbols, compiles the selected sources, and links them into one `nvidiafb.o` module or built-in object.

## State and Persistence Behavior

The file owns no runtime state. Its state is build-time object selection based on Kconfig symbols.

## Dependencies and Integration Points

It integrates with Linux Kbuild and the `CONFIG_FB_NVIDIA`, `CONFIG_FB_NVIDIA_I2C`, and `CONFIG_FB_NVIDIA_BACKLIGHT` symbols. The unconditional inclusion of `nv_of.o` means Open Firmware EDID probing is always linked into the NVIDIA fbdev driver, while I2C/backlight functionality is gated by config.

## Risks and Edge Cases

The object grouping must match declarations in `nv_proto.h`; enabling a prototype without linking the corresponding object would create link failures, while missing optional stubs would break configurations without I2C/backlight. Because `nvidiafb-objs := $(nvidiafb-y)` aliases a conditional variable, changes must preserve Kbuild's expected `*-objs` naming.

## Test Signals

Build-test `CONFIG_FB_NVIDIA=y/m` with and without `CONFIG_FB_NVIDIA_I2C` and `CONFIG_FB_NVIDIA_BACKLIGHT`, and verify that `nvidiafb.o` links with no unresolved references in each combination.
