<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-cx2584x-v4l.h -->
# sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-cx2584x-v4l.h

Purpose: private declaration for the CX25840/CX2584x routing update bridge.

Important APIs/types/functions: declares `pvr2_cx25840_subdev_update(struct pvr2_hdw *, struct v4l2_subdev *)`.

Control flow: hardware subdevice management includes this header and invokes the helper during dirty input commits.

State and persistence: no state.

Dependencies and integration: includes pvrusb2 hardware internals and V4L2 subdev type usage.

Risks: tight coupling to internal hardware state and direct subdevice update conventions.

Test signals: compile with CX25840 selected and verify routing helper linkage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-cx2584x-v4l.h -->
