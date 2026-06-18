<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-audio.h -->
# sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-audio.h

Purpose: private declaration for the MSP3400 audio-routing bridge.

Important APIs/types/functions: declares `pvr2_msp3400_subdev_update(struct pvr2_hdw *, struct v4l2_subdev *)`.

Control flow: hardware/subdevice code includes this header to call the MSP3400 update hook when pvrusb2 input state changes.

State and persistence: no state; it exposes a routing helper prototype.

Dependencies and integration: includes `pvrusb2-hdw-internal.h`, so it is private to the pvrusb2 hardware layer.

Risks: including the internal hardware header couples users to private layout rather than a narrow forward declaration.

Test signals: compile users that register MSP3400 clients; ensure the prototype matches `pvrusb2-audio.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-audio.h -->
