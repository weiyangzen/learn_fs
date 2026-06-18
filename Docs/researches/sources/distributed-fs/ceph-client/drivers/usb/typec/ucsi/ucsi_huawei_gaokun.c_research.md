# sources/distributed-fs/ceph-client/drivers/usb/typec/ucsi/ucsi_huawei_gaokun.c

## Purpose

`ucsi_huawei_gaokun.c` supports the Huawei MateBook E Go EC UCSI interface. It forwards EC UCSI mailboxes to the UCSI core and supplements incomplete firmware reporting with EC-side Type-C orientation, mux, DisplayPort pin assignment, and HPD bridge notifications.

## Important APIs, Types, and Functions

`struct gaokun_ucsi` owns the EC pointer, UCSI device, delayed registration work, notifier block, version, and port array. `struct gaokun_ucsi_port` stores per-port completion, lock, DP bridge, orientation, mux, pin assignment, SVID, and HPD bits. UCSI callbacks call `gaokun_ec_ucsi_read()` and `gaokun_ec_ucsi_write()`. `gaokun_ucsi_port_update()` decodes two-byte EC port records into Type-C/DP state. `gaokun_ucsi_refresh()` reads the EC aggregate register and updates the changed port. `gaokun_ucsi_notify()` handles EC USB and UCSI event classes.

## Control Flow

Probe reads the EC-reported port count, allocates per-port state, creates optional DP HPD bridges from child nodes, creates the UCSI object, and schedules delayed registration because the EC is unreliable early. The worker registers EC notifications and UCSI. EC UCSI events read CCI, call `ucsi_notify_common()`, then wait briefly for a matching USB event before forcing altmode handling. EC USB events complete all port USB acknowledgements and handle pending DP/HPD updates.

## State and Persistence Behavior

All state is runtime-only. Per-port locks protect decoded EC state used by connector callbacks. The delayed work acts as a boot-time stabilization mechanism; no firmware state is stored persistently.

## Dependencies and Integration Points

Dependencies include the `huawei-gaokun-ec` platform API, UCSI core, Type-C orientation APIs, USB PD/DP altmode definitions, DRM AUX HPD bridge helpers, auxiliary bus, firmware child-node `reg` properties, and EC PAN acknowledgement calls.

## Risks and Test Signals

Risks include EC register checksum/format assumptions, `GET_IDX()` returning no update, delayed UCSI registration failure leaving notifications absent, races between UCSI connector allocation and altmode events, and forced altmode enable when USB events are missing. Test signals include delayed registration, EC UCSI CCI notification, USB-event completion path, DP HPD bridge status transitions, orientation changes under `port->lock`, and removal cancelling delayed work before unregistering.
