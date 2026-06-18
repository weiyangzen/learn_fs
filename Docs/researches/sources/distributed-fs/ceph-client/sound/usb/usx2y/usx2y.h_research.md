<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/usx2y/usx2y.h -->
# sources/distributed-fs/ceph-client/sound/usb/usx2y/usx2y.h

## Purpose
Common constants for older TASCAM US-X2Y devices: driver version, hwdep IDs, hardware type IDs, USB product IDs, and chip-status flags.

## APIs, Types, and Functions
Defines `USX2Y_DRIVER_VERSION`, hwdep ID strings `SND_USX2Y_LOADER_ID` and `SND_USX2Y_USBPCM_ID`, type enum values for US-122/US-224/US-428, product IDs, and status flags `USX2Y_STAT_CHIP_INIT`, `USX2Y_STAT_CHIP_MMAP_PCM_URBS`, and `USX2Y_STAT_CHIP_HUP`.

## Control Flow, State, and Persistence
No runtime flow. These constants shape card identity, firmware-loader status reporting, PCM mode selection, and disconnect/hangup behavior across the US-X2Y driver.

## Dependencies and Integration
Included by `usbusx2y.c`, `usX2Yhwdep.c`, and audio/hwdep PCM code. It is the small shared identity/status contract for the legacy driver.

## Risks and Test Signals
Risks are ABI/name stability for hwdep IDs and status-bit meaning. Test signals are correct product classification, hwdep userspace discovering expected IDs, normal versus mmap PCM mode switching, and hangup behavior after disconnect.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/usx2y/usx2y.h -->
