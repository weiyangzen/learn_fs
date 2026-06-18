<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/auxdisplay/Makefile -->
# sources/distributed-fs/ceph-client/drivers/auxdisplay/Makefile

## Purpose

This Makefile maps auxdisplay Kconfig symbols to Kbuild objects. It is the build composition point for character LCDs, graphical LCDs, line displays, LED controllers, and panel drivers.

## Important APIs, types, and functions

There are no runtime APIs. Rules include `obj-$(CONFIG_ARM_CHARLCD) += arm-charlcd.o`, `CONFIG_CFAG12864B` building both core and framebuffer objects, `CONFIG_CHARLCD`, `CONFIG_HD44780_COMMON`, `CONFIG_HD44780`, `CONFIG_HT16K33`, `CONFIG_IMG_ASCII_LCD`, `CONFIG_KS0108`, `CONFIG_LCD2S`, `CONFIG_LINEDISP`, `CONFIG_MAX6959`, `CONFIG_PARPORT_PANEL`, and `CONFIG_SEG_LED_GPIO`.

## Control flow

Kbuild evaluates each `obj-*` assignment according to `.config`. Built-in values link into the kernel; module values build modules where supported.

## State and persistence behavior

No runtime state is stored. The file affects build artifacts only.

## Dependencies and integration points

It depends on symbols from the sibling Kconfig and integrates source files in `drivers/auxdisplay` into the kernel build.

## Risks

Object-name drift can silently omit a driver or break link. Multi-object entries like `cfag12864b.o cfag12864bfb.o` must stay aligned with code dependencies. Common-core objects must match Kconfig `select` relationships.

## Test signals

Build each auxdisplay symbol as module and built-in where allowed, verify expected `.o`/`.ko` outputs, and run clean rebuilds after renaming or moving driver files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/auxdisplay/Makefile -->
