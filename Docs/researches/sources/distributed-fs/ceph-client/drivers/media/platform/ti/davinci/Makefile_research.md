<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/davinci/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/platform/ti/davinci/Makefile

## Purpose

This Makefile connects DaVinci VPIF Kconfig symbols to the common VPIF core and capture/display driver objects.

## Important APIs, types, and functions

- `obj-$(CONFIG_VIDEO_DAVINCI_VPIF_DISPLAY) += vpif.o vpif_display.o`
- `obj-$(CONFIG_VIDEO_DAVINCI_VPIF_CAPTURE) += vpif.o vpif_capture.o`

## Control flow

There is no runtime flow. During kernel build, the selected config symbol determines whether `vpif.o` is linked with display and/or capture support.

## State and persistence behavior

It has no runtime state. Build outputs persist as kernel objects/modules.

## Dependencies and integration points

The file depends on the symbols from `Kconfig` and on source-level exports from `vpif.c` used by `vpif_capture.c` and `vpif_display.c`.

## Risks and edge cases

If both capture and display are enabled as modules, `vpif.o` is listed in both module links, so build-system behavior and symbol export expectations matter. The source relies on `vpif.c` being available before either functional driver can access global MMIO helpers.

## Test signals

Compile capture-only, display-only, and both-enabled configurations as modules and built-ins. Confirm module loading order exposes the common VPIF driver before capture/display stream operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/davinci/Makefile -->
