<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/ishtp-fw-loader.c -->
# sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/ishtp-fw-loader.c

## Purpose
`ishtp-fw-loader.c` implements an optional ISHTP client that loads main ISH firmware from the host filesystem into ISH SRAM through a shim firmware loader, then starts execution. It supports legacy ISHTP-fragment transfer and direct-DMA transfer.

## Important APIs, Types, and Functions
The loader binds a fixed GUID and defines loader commands `XFER_QUERY`, `XFER_FRAGMENT`, and `START`. Packed protocol structs include `loader_msg_hdr`, query/response formats, firmware/version/capability structs, IPC and DMA fragment formats, and start command. `struct response_info` coordinates synchronous command responses. `struct ishtp_cl_data` stores the client, response state, reset/load work, retry flag, and retry count. Key functions are `get_firmware_variant`, `loader_cl_send`, `process_recv`, `ish_query_loader_prop`, `ish_fw_xfer_ishtp`, `ish_fw_xfer_direct_dma`, `ish_fw_start`, `load_fw_from_host`, `loader_init`, reset/remove/probe callbacks, and module init/exit.

## Control Flow
Probe allocates client state and an ISHTP client, initializes wait/work structures, establishes a connection to the loader GUID, registers the RX callback, takes a device reference, and schedules firmware load work. Loading reads the `firmware-name` property from the parent PCI device, requests `intel/<name>`, queries shim capabilities with image size, validates max image size and DMA cacheline alignment, chooses direct DMA if supported else ISHTP, transfers fragments until the image is complete, then sends START. Retryable failures set `flag_retry`; the error path resets ISH and retries up to three attempts.

The send path installs the expected response buffer, sends through `ishtp_cl_send`, waits up to three seconds, validates callback-reported errors, and returns response size. RX processing validates response buffer presence, one outstanding response, minimum header size, command ID, max size, response bit, and firmware status before copying data and waking the waiter.

## State and Persistence Behavior
Firmware image data is transient from `request_firmware`. Loader response state persists per client and assumes one synchronous command outstanding. Work items persist for firmware loading and reset recovery. Direct DMA allocates a coherent buffer for each load attempt and frees it after transfer. Retry count persists until client reprobe/removal.

## Dependencies and Integration Points
The file depends on firmware_class, ISHTP client APIs, PCI parent device properties, DMA coherent allocation, cache flush APIs, and ISH hardware reset. It registers as an ISHTP client driver via `late_initcall`.

## Risks and Edge Cases
`get_firmware_variant` requires a `firmware-name` property; missing metadata makes loading fail. In direct DMA, payload size is rounded down to a cacheline boundary; if limits are smaller than one cacheline, zero-size allocation/progress would be hazardous. The code flushes a coherent DMA buffer, which is conservative but platform-sensitive. Only one outstanding loader command is supported. Some failures are retryable with full ISH reset, which can disrupt other clients.

## Test Signals
Signals include loader client enumeration, firmware-name property presence, successful query response, selected transfer mode, fragment ACKs for every offset, START ACK, retry behavior on injected transport failures, DMA buffer size/module parameter handling, and main ISH firmware version sysfs updates after load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/ishtp-fw-loader.c -->
