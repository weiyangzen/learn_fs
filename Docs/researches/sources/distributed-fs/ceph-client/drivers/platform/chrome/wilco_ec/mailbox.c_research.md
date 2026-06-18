<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/wilco_ec/mailbox.c -->
# sources/distributed-fs/ceph-client/drivers/platform/chrome/wilco_ec/mailbox.c

## Purpose

This file implements the Wilco EC mailbox transport over the MEC LPC interface. It provides the exported `wilco_ec_mailbox()` API used by Wilco sysfs, debugfs, telemetry, properties, keyboard LED, and other child drivers.

## Important APIs, Types, And Functions

`wilco_ec_response_timed_out()` polls host command flags until the EC is not pending/busy. `wilco_ec_checksum()` computes the 8-bit request checksum. `wilco_ec_prepare()` fills `struct wilco_ec_request`. `wilco_ec_transfer()` writes request header/data to MEC, starts the command with `EC_MAILBOX_START_COMMAND`, waits, validates flag/result/checksum/size, and copies response data. `wilco_ec_mailbox()` locks `ec->mailbox_lock`, prepares the request in the shared buffer, calls transfer, and exports the symbol.

## Control Flow

Callers fill `struct wilco_ec_message` with type, request data, response data, sizes, and optional no-response flag. The mailbox layer serializes the operation, writes request bytes to MEC offsets 0 and header-size, starts the EC command via the command IO port, optionally returns immediately for no-response commands, then reads a full response packet into `ec->data_buffer` and validates it.

## State And Persistence

The shared `ec->data_buffer` and mailbox registers are protected by `mailbox_lock`. There is no persisted kernel state. EC-side settings changed by commands persist according to EC firmware behavior. Timeout is bounded by `HZ`.

## Dependencies And Integration Points

It depends on Wilco platform data structs, `cros_ec_lpc_io_bytes_mec()`, IO port accessors, jiffies, and child drivers using the exported mailbox API.

## Risks

Response validation requires `rs->data_size == EC_MAILBOX_DATA_SIZE`, so protocol variants with shorter valid replies would fail. The checksum validation depends on `cros_ec_lpc_io_bytes_mec()` returning the checksum status convention used here. No-response commands bypass response validation entirely. Polling latency and timeout affect all Wilco EC clients.

## Test Signals

Test serialized concurrent mailbox clients, checksum failure, EC result failure, bad data size, short response, no-response command, busy timeout, IO read/write errors, and representative legacy/property/telemetry callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/wilco_ec/mailbox.c -->
