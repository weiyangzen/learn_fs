# sources/distributed-fs/ceph-client/drivers/staging/greybus/fw-download.c

## Purpose
Implements the Greybus firmware download protocol. It lets a module ask the AP to find a firmware blob by tag, fetch byte ranges by firmware ID, and release the firmware when done.

## Important APIs, Types, And Functions
`struct fw_download` owns the connection, parent device, firmware request list, ID allocator, and mutex. `struct fw_request` tracks one firmware blob, firmware ID, name, `struct firmware`, timeout work, release deadline, kref, and timeout/disabled flags. Handlers are `fw_download_find_firmware()`, `fw_download_fetch_firmware()`, `fw_download_release_firmware()`, dispatched by `gb_fw_download_request_handler()`. Connection lifecycle is `gb_fw_download_connection_init()/exit()`.

## Control Flow
Find validates request size and tag termination, allocates ID 1-255, builds a `gmp_...tag.tftf` name from interface identifiers, calls `request_firmware()`, lists the request, computes a release deadline, starts delayed timeout work, and returns firmware ID and size. Fetch looks up the ID with a kref, cancels current timeout work, verifies not disabled and within total timeout, bounds-checks offset and size, allocates a response, copies bytes, and refreshes the short timeout. Release cancels timeout work, removes the request, drops references, and releases the firmware.

## State And Persistence
Firmware contents are held by Linux firmware loader references until released or timed out. IDs are reused only when a request completes normally; timed-out IDs are deliberately leaked from the allocator to avoid stale module requests referring to a later request.

## Dependencies And Integration Points
Uses Linux firmware loading, IDA, delayed work, kref, jiffies, and Greybus request/response allocation. It depends on `firmware.h` naming constants and is initialized by `fw-core.c`.

## Risks
After 255 timed-out requests no more IDs can be allocated by design. Timeout races are managed by list mutex plus krefs, so changes must preserve that model. Fetch response sizes are module-controlled and must remain bounded by firmware size and operation allocation limits.

## Test Signals
Test valid find/fetch/release, unterminated tags, missing firmware, bad offsets/sizes, fetch after timeout, release after timeout, connection exit with pending requests, ID reuse after normal release, and exhausted IDs after repeated timeouts.
