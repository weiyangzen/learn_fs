<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/disp.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/disp.c

## Purpose
Implements the R535 RM-backed display engine, including display channels, output discovery, SOR/DP/HDMI/audio/backlight controls, hotplug/DP IRQ events, and vblank interrupt routing.

## Important APIs, Types, And Functions
Defines channel helpers for core/window/immediate/cursor channels, `r535_disp_chan_set_pushbuf`, `r535_dmac_alloc`, SOR HDMI/DP/HDA/backlight function tables, connector/output creation helpers, DP AUX/training/MST helpers, display event callbacks, `r535_disp_oneinit/init/fini/dtor`, `r535_disp_new`, and exports `r535_disp` API.

## Control Flow
Oneinit allocates display RAMIN, tells internal RM about instance memory, constructs RM client/device/display-common objects, queries static display info, optionally forwards ACPI brightness state, enables manual DisplayPort mode, queries head count/mask, creates head and SOR objects, queries supported display IDs, creates outputs/connectors through RM control calls, initializes an NVKM event object, registers RM hotplug and DP IRQ events, builds RAMHT, and registers a stall interrupt handler. Runtime channel init sets pushbuffer metadata with RM and allocates the corresponding RM channel object. Output operations call RM controls for detection, SOR assignment, active output inheritance, EDID, DP AUX, DP training, MST IDs, HDMI SCDC/audio, and backlight.

## State And Persistence
Persists display instance memory, RM client/device/object handles, `objcom`, hotplug/IRQ event handles, assigned SOR mask, heads, SORs, connectors, outputs, RAMHT, channel `suspend_put` offsets, and NVKM event state. Hardware vblank masks and display channel user areas are touched.

## Dependencies And Integration Points
Depends on NVKM display/head/IOR/output/channel frameworks, GSP RM allocation/control/device-event APIs, ACPI DSM for brightness data, RAMHT, VFN interrupt handling, and generation RM GPU display class data.

## Risks And Edge Cases
The file contains many RM protocol assumptions. Display ID to SOR inheritance must match RM state. DP AUX/training includes retry handling for RM-requested panel delays. Missing ACPI or RM support paths must fail gracefully. Channel suspend offsets are captured from MMIO and reused on resume.

## Test Signals
Working mode setting, hotplug and DP IRQ events, vblank interrupts, DP AUX/training, MST allocation, HDMI/DP audio, backlight get/set, suspend/resume channel restoration, and clean RM object teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/disp.c -->
