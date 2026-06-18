# `sources/distributed-fs/ceph-client/include/linux/usb/musb.h`

## Purpose

`musb.h` defines board/platform data and mode constants for Mentor Graphics MUSB HDRC controllers. It is the public configuration contract between platform glue and the MUSB core.

## Important APIs, Types, and Constants

- Mode constants describe undefined, host, peripheral, OTG, and dual-role operation.
- Power and endpoint limit constants describe MUSB capability and board power assumptions.
- `struct musb_hdrc_eps_bits` and endpoint configuration structures describe FIFO sizing and endpoint capabilities.
- `struct musb_hdrc_config` describes multipoint support, dynamic FIFO, soft connect, DMA mode, endpoint count, RAM bits, and FIFO configuration.
- `struct musb_hdrc_platform_data` carries mode, power budget, min power, platform-specific config pointer, board callbacks, and PHY/clock-related integration fields.

## Control Flow and Lifetimes

Platform glue fills `musb_hdrc_platform_data` and registers the controller. The MUSB core reads mode, FIFO, endpoint, and power data during probe, initializes PHY and controller registers, then exposes host, gadget, or OTG behavior depending on mode. The platform data must remain valid while the controller is active.

## State and Persistence Behavior

The header defines static controller configuration. Runtime role, endpoint queue, DMA, and PHY state live in the MUSB driver. Mode selection and FIFO layout persist for the driver instance.

## Dependencies and Integration Points

It integrates MUSB platform glue, USB host/gadget/OTG subsystems, PHY providers, and board power management. It is used by SoC-specific MUSB headers such as `musb-ux500.h`.

## Risks and Edge Cases

Incorrect FIFO or endpoint configuration can break enumeration or transfer scheduling. Host/peripheral/OTG mode mismatches with hardware wiring cause role-switch failures. Power budget fields affect bus power advertisements. Dynamic FIFO assumptions must match controller synthesis options.

## Test Signals

Build MUSB host, gadget, and OTG configurations; probe platform devices with static and dynamic FIFOs; run bulk/control/interrupt transfers; test VBUS/session changes, suspend/resume, disconnect/reconnect, and DMA fallback to PIO.
