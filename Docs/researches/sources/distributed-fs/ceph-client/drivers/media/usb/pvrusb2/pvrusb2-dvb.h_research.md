<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-dvb.h -->
# sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-dvb.h

Purpose: data model and prototypes for pvrusb2 DVB integration.

Important APIs/types/functions: defines `PVR2_DVB_BUFFER_COUNT` and `PVR2_DVB_BUFFER_SIZE`, `struct pvr2_dvb_adapter`, `struct pvr2_dvb_props`, and `pvr2_dvb_create()`.

Control flow: device descriptors provide `pvr2_dvb_props` attach callbacks; setup code calls `pvr2_dvb_create()` to register and manage the DVB side using the embedded channel and buffer arrays.

State and persistence: declares persistent runtime DVB adapter state: pvr2 channel, DVB adapter/demux/dmxdev/net, up to two frontends, I2C client handles, feed count, stream thread, lock, waitqueue, and 32 packet buffers.

Dependencies and integration: includes DVB frontend/demux/net/dmxdev headers and pvrusb2 context definitions.

Risks: fixed buffer count/size must match stream throughput expectations. The struct exposes multiple ownership domains whose teardown ordering is enforced only by implementation discipline.

Test signals: compile with DVB enabled; inspect adapter creation and stream buffer allocation under live DTV feeds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-dvb.h -->
