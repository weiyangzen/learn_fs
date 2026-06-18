# sources/distributed-fs/ceph-client/drivers/soc/qcom/wcnss_ctrl.c

## Purpose

`wcnss_ctrl.c` is an RPMSG control driver for Qualcomm WCNSS. It requests firmware version information, downloads the WLAN NV binary to the remote processor in fragments, waits for optional cold-boot completion, populates child devices, and exports an API for creating additional WCNSS RPMSG endpoints.

## Important APIs, Types, and Functions

`struct wcnss_ctrl` stores the RPMSG endpoint, completions, last ACK status, and async probe work. Packed message types model common headers, version responses, NV download requests, and NV download responses. Key functions are `wcnss_ctrl_smd_callback()`, `wcnss_request_version()`, `wcnss_download_nv()`, exported `qcom_wcnss_open_channel()`, `wcnss_async_probe()`, `wcnss_ctrl_probe()`, and `wcnss_ctrl_remove()`.

## Control Flow

Probe allocates state, initializes completions/work, stores drvdata, and schedules async work. The worker sends a version request and waits, loads `firmware-name` or the default NV file, fragments it into 3072-byte messages, waits for a download ACK, optionally waits for cold-boot-complete, then populates child platform devices. The RPMSG callback completes the relevant wait depending on incoming message type.

## State and Persistence Behavior

Runtime state is per RPMSG device. Firmware data is file-backed externally but only streamed; no driver-side persistence exists. Successful download changes remote WCNSS state. Remove cancels work and depopulates children.

## Dependencies and Integration Points

The file depends on RPMSG/SMD, firmware loader, OF platform population, completions, workqueues, and `linux/soc/qcom/wcnss_ctrl.h`. Other WCNSS child drivers call `qcom_wcnss_open_channel()` using this control object.

## Risks and Edge Cases

The callback dereferences `hdr->type` before verifying `count >= sizeof(*hdr)`. `wcnss_download_nv()` leaks the firmware reference if `kzalloc_flex()` fails after `request_firmware()`. Reused completions are not reinitialized before each request; current sequencing is serial but stale completions would be dangerous if retries are added. Pointer arithmetic on `const void *data` relies on compiler extensions. Fragment length uses `ssize_t left`; zero-length firmware would produce an empty last packet only if loop semantics are revisited.

## Test Signals

Test normal boot, missing firmware, custom firmware name, multi-fragment and single-fragment downloads, cold-boot and done-boot ACKs, malformed short RPMSG packets, invalid response sizes, timeout paths, remove while work is active, and endpoint creation by child drivers. Use leak detection on the allocation-failure path after firmware load.
