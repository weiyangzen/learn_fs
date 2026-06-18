# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/rzv2m_usb3drd.c

## Purpose

This file is a small Renesas RZ/V2M USB3 dual-role glue driver. It owns the parent DRD register block and reset control, populates child platform devices, and exports `rzv2m_usb3drd_reset()` so child host/peripheral drivers can switch reset state and peripheral/host mode consistently.

## Important APIs, Types, and Functions

- `rzv2m_usb3drd_reset(struct device *dev, bool host)` is exported GPL-only and is the main integration API. It looks up the parent `struct rzv2m_usb3drd` from driver data and manipulates `USB_PERI_DRD_CON`.
- `rzv2m_usb3drd_set_bit()` and `rzv2m_usb3drd_clear_bit()` are read-modify-write helpers for the DRD register block.
- `rzv2m_usb3drd_probe()` allocates state, records the DRD IRQ named `"drd"`, maps the register resource, obtains/deasserts the reset control, enables runtime PM, and calls `of_platform_populate()` for child devices.
- `rzv2m_usb3drd_remove()` depopulates children, drops runtime PM, disables PM, and asserts reset.
- OF match data binds `renesas,rzv2m-usb3drd`; the platform driver name is `rzv2m-usb3drd`.

## Control Flow

Probe is parent-first. It maps the shared DRD registers and stores them in driver data before child nodes are populated, which lets children retrieve the parent state. The reset line is deasserted and runtime PM is resumed before `of_platform_populate()` creates host/peripheral children.

The exported reset helper switches between host and peripheral. In host mode it clears `PERI_CON`, clears host reset, and asserts peripheral reset. In peripheral mode it sets `PERI_CON`, asserts host reset, and clears peripheral reset. Remove reverses the probe sequence by depopulating children, dropping PM, disabling PM, and asserting the DRD reset.

## State and Persistence Behavior

The driver's state is the parent `struct rzv2m_usb3drd`, defined in the public RZ/V2M USB3DRD header. This file uses its `dev`, `reg`, `drd_irq`, and `drd_rstc` fields. There is no persistent storage. Hardware state persists in the DRD control register and reset line until changed by this driver or a child invoking `rzv2m_usb3drd_reset()`.

## Dependencies and Integration Points

The file depends on platform resources, OF child population, reset controls, runtime PM, MMIO helpers, and `linux/usb/rzv2m_usb3drd.h`. It is directly integrated by `renesas_usb3.c` for RZ/V2M peripheral reset and DRD IRQ/register sharing. Host-side child drivers can use the same parent device and exported reset helper.

## Risks and Edge Cases

- The helper assumes `dev_get_drvdata(dev)` returns a valid parent DRD object; callers must pass the parent device, not an arbitrary child.
- Register updates are unlocked read-modify-write operations. If host and peripheral children call the exported helper concurrently, mode bits could race unless higher-level role switching serializes them.
- Probe obtains the `"drd"` IRQ but does not request it itself; children are expected to consume it from parent state.
- Error paths must keep reset and runtime PM balanced; `err_pm` and `err_rst` do this, but future changes around child population need the same ordering.

## Test Signals

Validation should cover successful parent probe with child population, missing IRQ/resource/reset error paths, runtime PM resume failure, child probe access to parent `reg` and `drd_irq`, host-to-peripheral and peripheral-to-host reset calls, remove cleanup order, and integration with RZ/V2M `renesas_usb3` role switching. Hardware-level tests should verify `PERI_CON`, `HOST_RST`, and `PERI_RST` bit transitions for both modes.
