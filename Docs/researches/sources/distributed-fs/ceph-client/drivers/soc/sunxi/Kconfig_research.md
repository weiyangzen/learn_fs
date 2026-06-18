# sources/distributed-fs/ceph-client/drivers/soc/sunxi/Kconfig

## Purpose

This Kconfig file defines Allwinner sunXi SoC support options for MBUS DMA quirks and SRAM controller support.

## Important APIs, Types, and Functions

`SUNXI_MBUS` is a bool defaulting to `ARCH_SUNXI`, depending on `ARM || ARM64`. `SUNXI_SRAM` is a bool defaulting to `ARCH_SUNXI` and selecting `REGMAP_MMIO`.

## Control Flow

When enabled, these symbols cause the Makefile to build `sunxi_mbus.o` and/or `sunxi_sram.o`. The defaults enable both for Allwinner platforms while permitting explicit disable if dependencies allow.

## State and Persistence Behavior

The file has no runtime state. It controls compile-time inclusion.

## Dependencies and Integration Points

It integrates with architecture selection, DMA quirk setup, SRAM controller code, and regmap MMIO support.

## Risks and Edge Cases

`SUNXI_MBUS` is not user-visible in the snippet and depends on platform matching at runtime; wrong defaults could omit DMA offset fixups for old DTs. `SUNXI_SRAM` selects regmap support because the driver exposes syscon-style regmaps for selected registers.

## Test Signals

Validate ARM and ARM64 Allwinner defconfigs, non-Sunxi builds, and compile-test combinations. Confirm expected objects appear in build logs.
