# sources/distributed-fs/ceph-client/drivers/media/platform/amlogic/c3/Kconfig

## Purpose

This C3 Kconfig file sources the media blocks for the Amlogic C3 SoC family: ISP, MIPI adapter, and MIPI CSI-2 receiver.

## Important APIs, Types, And Symbols

- Sources `drivers/media/platform/amlogic/c3/isp/Kconfig`.
- Sources `drivers/media/platform/amlogic/c3/mipi-adapter/Kconfig`.
- Sources `drivers/media/platform/amlogic/c3/mipi-csi2/Kconfig`.

## Control Flow

Kconfig recursively evaluates the three child files when the Amlogic C3 subtree is loaded. Runtime behavior is entirely in the selected child drivers.

## State And Persistence

Only child Kconfig selections persist in `.config`.

## Dependencies And Integration Points

This file aligns with `amlogic/c3/Makefile`, which descends into the same three child directories. The C3 ISP capture code researched here depends on the ISP child symbol.

## Risks

Wrong child paths or missing source lines can break visibility for a pipeline component, which is especially important because ISP capture requires upstream C3 media entities to form a working pipeline.

## Test Signals

Run `make menuconfig` and confirm ISP, MIPI adapter, and CSI-2 entries are visible under Amlogic C3 when their dependencies are met.
