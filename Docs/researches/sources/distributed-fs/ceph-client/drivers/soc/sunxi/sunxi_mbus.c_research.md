# sources/distributed-fs/ceph-client/drivers/soc/sunxi/sunxi_mbus.c

## Purpose

`sunxi_mbus.c` installs DMA offset quirks for older Allwinner devices that perform DMA over the MBUS and lack modern interconnect descriptions in device tree.

## Important APIs, Types, and Functions

`sunxi_mbus_devices[]` lists compatible strings for display-engine virtual devices and MBUS-connected DMA clients. `sunxi_mbus_notifier()` handles platform bus add-device notifications. `sunxi_mbus_nb` registers that callback. `sunxi_mbus_platforms[]` limits activation to known Allwinner machine compatibles. `sunxi_mbus_init()` is an `arch_initcall`.

## Control Flow

At arch init, the driver checks whether the running machine matches a supported Allwinner platform. If so, it registers a platform bus notifier. For each newly added platform device, the notifier ignores non-add events, ignores devices whose OF compatible is not in `sunxi_mbus_devices`, and ignores devices that already have an `interconnects` property. For old bindings, it calls `dma_direct_set_offset(dev, PHYS_OFFSET, 0, SZ_4G)` so DMA address 0 maps to physical `PHYS_OFFSET` across a 4 GiB window.

## State and Persistence Behavior

State is limited to the registered notifier. The DMA offset becomes persistent per device for the device lifetime and affects all subsequent direct DMA mapping operations.

## Dependencies and Integration Points

It depends on OF machine/device compatible matching, platform bus notifiers, direct DMA mapping internals, and `PHYS_OFFSET`. It integrates legacy Allwinner display/video/camera devices with the DMA API.

## Risks and Edge Cases

The compatibility lists are manually curated; missing a device can produce broken DMA on old DTs. Applying the quirk to a device with a correct interconnect path would be wrong, hence the `interconnects` skip. Notifier registration has no unregister path because this is built-in init code. The 4 GiB window and `PHYS_OFFSET` assumptions must match the SoC memory map.

## Test Signals

Boot older and newer Allwinner DTs and verify devices without `interconnects` receive the expected DMA offset while modern DTs do not. Exercise DRM, video-engine, and CSI DMA, especially on systems with nonzero RAM base.
