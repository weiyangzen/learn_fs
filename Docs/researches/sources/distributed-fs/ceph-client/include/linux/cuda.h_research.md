<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cuda.h -->
# sources/distributed-fs/ceph-client/include/linux/cuda.h

## Purpose

`cuda.h` declares interfaces for Apple CUDA microcontroller support, which controls ADB, power, RTC, and related system functions on supported machines. The source was read as a complete 23-line file.

## Important APIs, Types, and Functions

It declares `find_via_cuda()`, `cuda_request(struct adb_request *req, void (*done)(struct adb_request *), int nbytes, ...)`, `cuda_poll()`, `cuda_get_time()`, and `cuda_set_rtc_time(struct rtc_time *tm)`.

## Control Flow

Platform initialization probes for VIA CUDA. Drivers submit variable-length CUDA/ADB requests with an optional completion callback. Polling services the controller where interrupt-driven flow is unavailable or during early boot. RTC helpers read and set controller-backed time.

## State and Persistence Behavior

Runtime state is maintained by the CUDA driver and request objects, while RTC time persists in controller hardware. The header owns no storage.

## Dependencies and Integration Points

It depends on `linux/rtc.h` and UAPI CUDA definitions, and references `struct adb_request`. It integrates with PowerMac/ADB input, platform power control, RTC, and early machine discovery.

## Risks and Edge Cases

Variable-argument request construction must match CUDA command packet formats. Polling and callback completion must avoid races. RTC conversion must handle controller-specific epoch/range behavior. Unsupported machines should fail probe cleanly.

## Test Signals

Signals include CUDA probe on supported PowerMac hardware, ADB request/response tests, callback completion ordering, polling-mode operation, RTC get/set round trips, and unsupported-platform build/probe behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cuda.h -->
