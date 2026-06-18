<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-context.h -->
# sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-context.h

Purpose: private declarations for pvrusb2 central context and channel management.

Important APIs/types/functions: defines `struct pvr2_context_stream`, `struct pvr2_context`, and `struct pvr2_channel`, plus prototypes for context creation/disconnect/global init/done, channel init/done/input limits/stream claims, and MPEG stream creation.

Control flow: higher-level interfaces embed or allocate `pvr2_channel`, initialize it against a `pvr2_context`, optionally set `check_func`, claim `video_stream`, and release it on teardown.

State and persistence: declares the fields that persist for device lifetime: linked-list pointers, hardware pointer, video stream wrapper, context mutex, notify/initialized/disconnect flags, per-channel stream/input mask/check callback.

Dependencies and integration: includes Linux mutex/USB/workqueue and forward-declares hardware/stream/ioread objects. It is the ABI between main hardware setup and pvrusb2 interface layers.

Risks: list linkage is open-coded rather than `list_head`, so pointer maintenance bugs are easy. Channel callbacks execute from the global context thread and must avoid blocking indefinitely.

Test signals: compile all pvrusb2 interfaces; static checks for channel lifecycle pairing; runtime open/close/disconnect tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-context.h -->
