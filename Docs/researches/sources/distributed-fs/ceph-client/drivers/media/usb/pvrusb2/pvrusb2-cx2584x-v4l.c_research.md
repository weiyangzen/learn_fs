<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-cx2584x-v4l.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-cx2584x-v4l.c

Purpose: routing bridge between pvrusb2 input selections and the CX25840/CX2584x audio/video decoder subdevice.

Important APIs/types/functions: `struct routing_scheme_item` pairs video and audio route values. Multiple routing tables cover Hauppauge, GotView, AV400, and HVR-160xxx schemes. `pvr2_cx25840_subdev_update()` validates the scheme/input and calls video and audio `s_routing()`.

Control flow: when input state is dirty or forced, the update function chooses the route table from `hdw->hdw_desc->signal_routing_scheme`, validates `hdw->input_val`, logs selected routes, and programs both video and audio routes on the decoder subdevice.

State and persistence: no local state. It programs persistent subdevice routing state and reads `struct pvr2_hdw` device descriptor/current input flags.

Dependencies and integration: depends on `cx25840` driver interface constants, V4L2 subdev audio/video ops, and pvrusb2 hardware internals. Called by the hardware layer during control commits.

Risks: direct `sd->ops->video/audio->s_routing` calls assume ops exist. Routing tables are hardware-specific and stale values can break audio/video capture silently. Invalid routes only log and skip updates.

Test signals: switch all inputs on 24xxx, GotView, AV400, and HVR-16xxxx devices; verify decoder status logs and actual captured video/audio source; enable chip trace logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-cx2584x-v4l.c -->
