<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-audio.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-audio.c

Purpose: routes pvrusb2 input selections to the MSP3400 audio subdevice.

Important APIs/types/functions: `routing_scheme0[]` maps pvrusb2 input control values to `MSP_INPUT()` routes. `pvr2_msp3400_subdev_update()` is the exported update hook called by hardware/subdevice management when input routing is dirty.

Control flow: when `hdw->input_dirty` or `force_dirty` is set, the function looks up the device routing scheme, validates `input_val`, computes the MSP input, and calls `sd->ops->audio->s_routing()` with a DSP SCART output route.

State and persistence: no private state. It reads `struct pvr2_hdw` fields and programs the MSP3400 subdevice, whose state persists until another route change or reset.

Dependencies and integration: depends on pvrusb2 hardware internals, debug tracing, `msp3400` driver interface macros, and V4L2 subdev audio routing.

Risks: only `PVR2_ROUTING_SCHEME_HAUPPAUGE` is represented. Invalid routing/input combinations are logged and skipped, leaving stale audio route state. The code calls subdev ops directly without NULL checks, relying on registration to match capabilities.

Test signals: switch TV/radio/composite/S-video inputs on 29xxx-style devices; enable `PVR2_TRACE_CHIPS`; verify audio follows the selected source and invalid routing schemes warn.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-audio.c -->
