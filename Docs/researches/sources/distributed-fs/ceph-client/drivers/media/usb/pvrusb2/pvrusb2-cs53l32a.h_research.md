<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-cs53l32a.h -->
# sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-cs53l32a.h

Purpose: private declaration for the CS53L32A audio-routing bridge.

Important APIs/types/functions: declares `pvr2_cs53l32a_subdev_update()`.

Control flow: hardware subdevice update code calls this helper when input routing changes on devices using the CS53L32A.

State and persistence: no state.

Dependencies and integration: includes pvrusb2 hardware internals and references V4L2 subdev types.

Risks: private-header coupling and direct reliance on internal `struct pvr2_hdw` layout.

Test signals: compile with CS53L32A selected and exercise OnAir routing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-cs53l32a.h -->
