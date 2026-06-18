<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/ati_remote2.c -->
## sources/distributed-fs/ceph-client/drivers/input/misc/ati_remote2.c

Purpose: USB input driver for the ATI/Philips Remote Wonder II RF remote, including mouse pad motion, per-mode key maps, channel/mode filtering, autosuspend, reset, and sysfs configuration.

Important APIs/types/functions: `struct ati_remote2` owns two USB interfaces/endpoints/URBs, coherent buffers, input device, per-mode keycode table, channel/mode masks, current mode, and flags. `ati_remote2_probe()` claims both interfaces, initializes URBs, configures receiver channel, and registers input. `ati_remote2_complete_mouse()` and `ati_remote2_complete_key()` resubmit interrupt URBs after decoding. `getkeycode`/`setkeycode` expose per-mode remapping.

Control flow and state: probe handles only interface 0, claims interface 1, validates endpoints, and creates separate interrupt URBs for mouse and key reports. Input open resumes USB and submits URBs unless suspended; close kills them. Completion handlers parse channel/mode, filter masks, report REL_X/Y or key press/release/repeat, and resubmit. Suspend/reset paths kill and restart URBs under a global mutex.

State and persistence behavior: module parameters seed `channel_mask` and `mode_mask`; sysfs can update runtime masks, with channel changes also sent by vendor control request. Keymaps live in memory and can be changed via input keymap APIs. USB receiver channel setting must be restored after reset resume.

Dependencies and integration points: depends on USB input, coherent DMA URBs, USB autosuspend, vendor control messages, input keymap APIs, module parameters, and device attribute groups.

Risks: uses a global mutex across all devices. Some error paths log and continue resubmitting URBs. Mode-key filtering has device-specific quirks. `setkeycode` can set invalid keycodes if input core does not prevalidate. Two-interface ownership makes disconnect/reset ordering important.

Test signals: verify two-interface probing, endpoint validation, open/close URB lifecycle, channel/mode module and sysfs masks, vendor channel setup, mouse reports, key press/release/repeat timing, key remapping, suspend/resume, reset_resume, and disconnect while open.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/ati_remote2.c -->
