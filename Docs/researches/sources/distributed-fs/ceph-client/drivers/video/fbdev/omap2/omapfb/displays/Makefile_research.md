# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/displays/Makefile

## Purpose
This Makefile maps OMAP2 fbdev display Kconfig symbols to connector, encoder, and panel object files.

## Important APIs, Types, And Functions
- Each `obj-$(CONFIG_FB_OMAP2_...)` line builds one display module.
- It covers the files in this work item plus additional Sony/TPO panel drivers not assigned here.

## Control Flow
The kernel build includes only objects whose config symbols are enabled.

## State And Persistence
No runtime state.

## Dependencies And Integration Points
It couples `displays/Kconfig` to actual source files and module names.

## Risks
Symbol/file mismatch would produce missing driver builds. Adding or renaming a display source requires synchronized Kconfig and Makefile edits.

## Test Signals
Build with each display option as module should produce the corresponding `.ko`/object and module alias metadata.
