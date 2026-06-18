# sources/distributed-fs/ceph-client/drivers/usb/typec/ucsi/ucsi_yoga_c630.c

## Purpose

`ucsi_yoga_c630.c` adapts the Lenovo Yoga C630 EC UCSI implementation to Linux. It compensates for firmware quirks around DisplayPort alternate modes, duplicate partner altmodes, current CAM reporting, orientation, and HPD events.

## Important APIs, Types, and Functions

`struct yoga_c630_ucsi` holds the Lenovo EC, UCSI object, optional DP HPD bridge, notifier block, and UCSI version. Read callbacks use `yoga_c630_ec_ucsi_read()` to fetch CCI and message-in data; control writes pass commands to `yoga_c630_ec_ucsi_write()`. `yoga_c630_ucsi_sync_control()` fakes connector-1 DP altmode data, suppresses connector-2 altmode results, and fixes off-by-one current CAM responses. `yoga_c630_ucsi_read_port0_status()` reads the EC USB mux register, updates orientation, and notifies the HPD bridge.

## Control Flow

Probe allocates state, creates a DP HPD bridge only for child port 0, creates the UCSI object, reads EC UCSI version, registers an EC notifier, registers UCSI, and then adds the bridge. EC USB or HPD events update port-0 mux state and signal connector change. EC UCSI events read CCI and call `ucsi_notify_common()`.

## State and Persistence Behavior

The driver stores only runtime pointers and the reported UCSI version. Orientation and HPD are recomputed from the EC mux register on notifications. There is no persistent configuration.

## Dependencies and Integration Points

It integrates with `lenovo-yoga-c630` EC platform data, UCSI core, Type-C class, USB Type-C DP definitions, DRM AUX HPD bridge helpers, auxiliary bus, and firmware child-node `reg` properties.

## Risks and Test Signals

Risks include hard-coded assumptions that only connector 1 supports DP, EC altmode duplication hiding real data, off-by-one CAM adjustment underflow, and notification ordering between HPD and UCSI. Test signals include fake DP altmode query on connector 1, ignored altmode query on connector 2, duplicate SOP altmode trimming, mux register orientation mapping, HPD bridge notifications, and unwind after UCSI or bridge registration failure.
