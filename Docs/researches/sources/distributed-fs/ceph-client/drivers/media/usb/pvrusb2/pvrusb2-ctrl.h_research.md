<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-ctrl.h -->
# sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-ctrl.h

Purpose: public internal API for pvrusb2 control access and symbolic conversion.

Important APIs/types/functions: defines `enum pvr2_ctl_type` (`int`, `enum`, `bitmask`, `bool`) and declares setters/getters, metadata accessors, V4L mapping helpers, custom symbol helpers, generic symbol parse/format functions, and the internal no-lock formatter.

Control flow: interface layers include this header to translate user-visible controls into pvrusb2 hardware-control operations.

State and persistence: no state; it forward-declares `struct pvr2_ctrl` and describes operations on hardware-owned controls.

Dependencies and integration: used across pvrusb2 V4L2/sysfs/control code. The internal formatter is intended for callers already inside the hardware critical region.

Risks: callers must distinguish `pvr2_ctrl_value_to_sym_internal()` from the locking wrapper or risk missing synchronization. V4L IDs are optional and may be zero.

Test signals: compile all control users; static analysis for internal formatter calls; V4L2 control enumeration and sysfs symbolic control tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-ctrl.h -->
