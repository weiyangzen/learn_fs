<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/wilco_ec/telemetry.c -->
# sources/distributed-fs/ceph-client/drivers/platform/chrome/wilco_ec/telemetry.c

## Purpose

This optional module exposes a constrained Wilco EC telemetry character device `/dev/wilco_telemN`. Userspace writes an allowlisted telemetry request and then reads the raw EC response from the same open file.

## Important APIs, Types, And Functions

`struct wilco_ec_telem_request` describes command and arguments. `check_telem_request()` allowlists command codes and validates argument size and reserved fields. `struct telem_device_data` owns the cdev/device and EC pointer. `struct telem_session_data` stores one open-file request/response and `has_msg`. `telem_open()`, `telem_write()`, `telem_read()`, and `telem_release()` implement the device semantics.

## Control Flow

Module init registers the class, major range, and platform driver. Probe allocates a minor and cdev for a core-created `wilco_telem` platform child. Only one process can open the device. A write copies and validates the request, sends a `WILCO_EC_MSG_TELEMETRY` mailbox command, stores a full 32-byte response, and marks it readable. A read copies a caller-selected byte count up to the response size and clears `has_msg`.

## State And Persistence

Device state is per minor; session state is per open file. Telemetry responses are volatile and overwritten by the next write in the same session. No EC telemetry is persisted by the driver.

## Dependencies And Integration Points

It depends on cdev/device core, IDA minor allocation, userspace copy helpers, Wilco mailbox, and the core platform child that passes `struct wilco_ec_device` as platform data.

## Risks

Only one opener is allowed, so long-lived clients can block diagnostics. `telem_read()` rejects counts greater than response size and returns exactly the requested count, not necessarily the whole response. The allowlist must stay aligned with EC firmware to avoid rejecting useful safe requests or permitting unsafe ones.

## Test Signals

Test class/major setup, single-open enforcement, all allowlisted commands, invalid reserved byte, oversized writes, PPID `always1` validation, mailbox short response rejection, read-before-write, partial reads, and device removal with open sessions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/wilco_ec/telemetry.c -->
