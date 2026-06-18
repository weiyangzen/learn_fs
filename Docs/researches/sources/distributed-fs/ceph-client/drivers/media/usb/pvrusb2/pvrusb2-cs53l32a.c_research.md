<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-cs53l32a.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-cs53l32a.c

Purpose: audio-routing bridge for CS53L32A ADC subdevices on pvrusb2 OnAir hardware.

Important APIs/types/functions: `routing_scheme1[]` maps pvrusb2 input values to CS53L32A input numbers. `pvr2_cs53l32a_subdev_update()` validates the routing scheme and calls `sd->ops->audio->s_routing()`.

Control flow: on dirty or forced input state, the function selects the route for `PVR2_ROUTING_SCHEME_ONAIR`; invalid scheme/input logs a warning and leaves the current subdevice route unchanged.

State and persistence: no local state. It reads `hdw->input_val` and programs subdevice state.

Dependencies and integration: depends on pvrusb2 hardware internals, V4L2 subdev audio ops, and trace logging.

Risks: only OnAir routing is supported. Direct subdev op calls assume the audio operation exists. Invalid inputs leave stale audio selection.

Test signals: OnAir Creator/USB2 analog input switching; trace logs; audio capture from TV/radio/composite/S-video paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-cs53l32a.c -->
