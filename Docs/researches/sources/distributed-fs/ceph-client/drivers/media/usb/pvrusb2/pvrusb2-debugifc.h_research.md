<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-debugifc.h -->
# sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-debugifc.h

Purpose: declarations for the pvrusb2 debug interface.

Important APIs/types/functions: declares `pvr2_debugifc_print_info()`, `pvr2_debugifc_print_status()`, and `pvr2_debugifc_docmd()`.

Control flow: sysfs/debug frontend code calls these functions to render state and execute commands against a `struct pvr2_hdw`.

State and persistence: no state; commands may mutate hardware through the implementation.

Dependencies and integration: forward-declares `struct pvr2_hdw` and keeps the debug frontend decoupled from full hardware internals.

Risks: comments distinguish synchronized and nonintrusive status paths; callers should choose the right printer for wedged hardware.

Test signals: compile debug interface users and exercise sysfs read/write paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-debugifc.h -->
