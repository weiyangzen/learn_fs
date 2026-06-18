# sources/distributed-fs/ceph-client/drivers/gpu/drm/mgag200/mgag200_bmc.c

## Purpose
Implements coordination with a server BMC that may remotely scan out the same Matrox framebuffer during mode changes.

## Important APIs, types, and functions
- `mgag200_bmc_stop_scanout()` signals an upcoming mode change, masks remote scan requests, and waits for remote scan/frame status.
- `mgag200_bmc_start_scanout()` resets remote-head level 2, unmasks scan requests, and clears the GPIO signal.

## Control flow
Stop scanout configures DAC GPIO misc bit 0 as output, drives it high to notify the BMC, sets `MGA1064_SPAREREG` bit 7 to mask remote scan requests, waits for `remhsyncsts` to go low, and if active waits for `remvsyncsts`. Start scanout asserts/deasserts `rstlvl2`, clears the scan request mask, and drives the misc line low again.

## State and persistence
State is stored in DAC indirect GPIO, spare, and remote-head control registers. These bits persist until start/stop toggles them or firmware/hardware changes them.

## Dependencies and integration points
Called by the BMC-aware VGA encoder helper in `mgag200_vga_bmc.c` when `mdev->info->sync_bmc` is true. Uses DAC register access macros from `mgag200_drv.h` and polling helpers.

## Risks
The protocol uses undocumented/board-specific DAC GPIO bits and timeout-based polling. If the BMC does not follow the expected handshake, stop may time out and return without guaranteeing scanout quiescence. Register access must be serialized by the caller's modeset lock path.

## Test signals
Server platforms with active BMC remote console should modeset without tearing or BMC lockups. Poll timeout behavior, remote console continuity, and correct restoration after disable/enable are key signals.
