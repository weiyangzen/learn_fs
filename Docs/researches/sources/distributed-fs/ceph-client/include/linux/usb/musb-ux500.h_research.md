# `sources/distributed-fs/ceph-client/include/linux/usb/musb-ux500.h`

## Purpose

`musb-ux500.h` provides platform glue declarations for the UX500 variant of the Mentor USB MUSB controller. It exists so board/platform code and the MUSB driver can exchange UX500-specific resources.

## Important APIs, Types, and Constants

- The header is intentionally small and primarily declares the UX500 platform interface consumed by the MUSB glue driver.
- It sits next to `musb.h`, which defines the generic MUSB platform data and mode constants.

## Control Flow and Lifetimes

Platform code registers the UX500 MUSB device and passes platform data/resources to the glue driver. The glue driver then initializes the generic MUSB core with UX500-specific clocks, interrupts, DMA, and mode configuration.

## State and Persistence Behavior

No direct state is stored in this header. Runtime state is in the UX500 glue driver and generic MUSB core.

## Dependencies and Integration Points

It integrates ST-Ericsson UX500 platform code with `drivers/usb/musb/` and the generic `musb_hdrc_platform_data` contract from `musb.h`.

## Risks and Edge Cases

The main risk is platform/API drift: if the UX500 glue driver expects fields or callbacks not matched by board code, probe fails or role switching is broken. Because the header is glue-only, test coverage must come from platform driver builds.

## Test Signals

Build UX500 MUSB glue, probe on relevant platform/device-tree configuration, exercise host/peripheral mode, suspend/resume, and DMA/PIO transfer paths through the generic MUSB core.
