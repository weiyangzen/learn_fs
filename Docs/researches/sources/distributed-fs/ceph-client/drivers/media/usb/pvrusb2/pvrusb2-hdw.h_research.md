# sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-hdw.h

Purpose: public hardware API for the pvrusb2 driver. It exposes an opaque `struct pvr2_hdw`, control IDs, input constants, stream configuration types, master-state constants, and the operations used by V4L2, sysfs, context, DVB, debug, and lower-level helper modules.

Important APIs, types, and functions: defines internal control IDs such as `PVR2_CID_STDCUR`, `PVR2_CID_INPUT`, `PVR2_CID_FREQUENCY`, crop capability IDs, and `PVR2_CID_STDDETECT`. Defines input values for TV, DTV, composite, S-video, and radio; `enum pvr2_config` for MPEG/VBI/PCM/raw stream configuration; `enum pvr2_v4l_type` for minor-number slots; and master states `PVR2_STATE_DEAD` through `PVR2_STATE_RUN`. Public functions cover creation, initialization, teardown, disconnect, V4L device hookup, unit/USB/serial/bus/identity lookup, control enumeration, control lookup by index/internal ID/V4L ID, control commit, input availability/allowed masks, tuner/crop/status polling, USB speed query, type/description lookup, streaming control, stream-type control, video stream retrieval, CPU firmware/EEPROM debug retrieval, V4L minor storage, control-message/register/GPIO helpers, debug state reports, module status logging, and encoder firmware upload.

Control flow: callers create a hardware handle in USB probe, initialize it with a state callback, attach user-facing interfaces, commit controls after updates, start/stop streaming through the state machine, and disconnect/destroy on USB removal. Lower-level helpers use the same header for register and GPIO commands that are intentionally not part of normal user-facing control flow.

State and persistence: the header hides all state inside `struct pvr2_hdw`. It communicates state through getters, control handles, stream handles, and debug reports. No persistent storage is declared here.

Dependencies and integration points: includes Linux USB/V4L2 declarations, `pvrusb2-io.h` for `struct pvr2_stream`, and `pvrusb2-ctrl.h` for control access. It is the principal contract between hardware core and pvrusb2 context, sysfs, V4L2, DVB, encoder, I2C, and debug code.

Risks: low-level APIs such as `pvr2_send_request()`, `pvr2_write_register()`, GPIO changes, CPU reset, and firmware upload can disrupt hardware state and must be serialized by implementation expectations. Minor-number storage is explicitly a V4L coupling inside hardware state. State values are numeric and used by controls/sysfs, so changing them has user-visible effects.

Test signals: compile all callers after prototype changes; probe/remove devices; verify state names through controls and debug; run V4L2 open/register/minor paths; exercise debug firmware and GPIO functions only on controlled hardware.
