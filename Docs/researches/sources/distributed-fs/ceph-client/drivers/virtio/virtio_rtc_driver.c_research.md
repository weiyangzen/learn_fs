## sources/distributed-fs/ceph-client/drivers/virtio/virtio_rtc_driver.c

Purpose: this is the virtio RTC core driver. It negotiates virtio clock devices, owns request and alarm virtqueues, implements typed virtio RTC request wrappers, registers RTC/PTP user-facing clocks, and handles suspend/resume and removal.

Important APIs/types/functions: `struct viortc_dev` stores `virtio_device`, optional RTC class wrapper, virtqueues, PTP handles, alarm buffers, and clock count. `struct viortc_msg` represents one request/response transaction with devm buffers, a completion, response length, and a two-reference lifetime model. Public internal helpers include `viortc_read()`, `viortc_read_cross()`, `viortc_cross_cap()`, `viortc_read_alarm()`, `viortc_set_alarm()`, and `viortc_set_alarm_enabled()`. Probe/remove and PM hooks are `viortc_probe()`, `viortc_remove()`, `viortc_freeze()`, and `viortc_restore()`.

Control flow: probe allocates device state, finds request and optional alarm queues, marks the device ready, requests configuration, enumerates each clock, and registers RTC/PTP representations where supported. Request helpers allocate a message, populate little-endian fields through macros, add request/response scatterlists to the request queue, kick the device, wait for completion with optional timeout, validate response status and size, extract fields, and drop the caller reference. Alarm queue callbacks validate notification headers, dispatch valid alarm notifications to the RTC class wrapper, requeue the buffer, and notify the device if needed.

State and persistence behavior: all allocations are device-managed. Request messages survive timeout by retaining the callback reference until a late response or device cleanup. Clock exposure state is kept in `viortc_class` and `clocks_to_unregister`; removal unregisters PTP clocks and stops RTC ops before resetting the virtio device.

Dependencies and integration points: depends on virtio core, virtqueue APIs, `uapi/linux/virtio_rtc.h`, RTC class support, PTP support, and optional alarm feature negotiation through `VIRTIO_RTC_F_ALARM`.

Risks: request timeouts leave messages for late callback release, so refcount correctness is critical. `viortc_restore()` assumes alarm queue indexes only when alarms are supported and must be exercised in non-alarm configurations. Response validation rejects any short or over/under-sized response, making spec conformance important.

Test signals: probe devices with zero, one, and multiple clocks; UTC-like RTC registration; PTP registration; alarm feature negotiation and notifications; request timeout/interrupt handling; suspend/resume with wake alarms; malformed response sizes/statuses; and remove during pending request.
