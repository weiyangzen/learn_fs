<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-encoder.h -->
# sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-encoder.h

Purpose: public internal prototypes for pvrusb2 CX23416 encoder operations.

Important APIs/types/functions: declares `pvr2_encoder_adjust()`, `pvr2_encoder_configure()`, `pvr2_encoder_start()`, and `pvr2_encoder_stop()`.

Control flow: hardware state-machine code calls configure after firmware/subdevice setup, adjust after control changes, and start/stop around stream transitions.

State and persistence: no state in the header; functions operate on `struct pvr2_hdw`.

Dependencies and integration: forward-declares `struct pvr2_hdw`, keeping callers independent of implementation details.

Risks: callers must ensure encoder firmware is loaded and hardware locks/state permit commands.

Test signals: compile hardware users and run stream lifecycle tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-encoder.h -->
