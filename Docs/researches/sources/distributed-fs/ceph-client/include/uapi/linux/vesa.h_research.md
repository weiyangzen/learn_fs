# sources/distributed-fs/ceph-client/include/uapi/linux/vesa.h

## Purpose
Defines VESA display blanking/power-management mode values for userspace-facing video APIs.

## Important APIs, Types, And Constants
`enum vesa_blank_mode` exposes `VESA_NO_BLANKING`, `VESA_VSYNC_SUSPEND`, `VESA_HSYNC_SUSPEND`, `VESA_POWERDOWN` as the OR of vsync and hsync suspend, and `VESA_BLANK_MAX`. The header also defines same-named preprocessor aliases for compatibility with code expecting macros.

## Control Flow, State, And Persistence
There is no executable code. Userspace or framebuffer/video drivers pass these values to blanking paths; hardware state changes to no blanking, sync suspend, or powerdown until another mode is set.

## Dependencies And Integration Points
The header is standalone. It integrates with display/framebuffer/video blanking controls and legacy tools that use VESA DPMS-style values.

## Risks And Test Signals
Risks are limited but include enum/macro name collisions and drivers interpreting powerdown bits inconsistently. Tests should compile consumers with both enum and macro references, set each blanking mode on a supported device, and verify display power/sync behavior or driver state reporting.
