<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/pfr_telemetry.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/pfr_telemetry.c

## Purpose
`pfr_telemetry.c` exposes the ACPI Platform Firmware Runtime Telemetry interface for devices matching `INTC1081`. It lets userspace configure firmware log level/type, query log buffer metadata through `_DSM`, and mmap the firmware telemetry buffer read-only.

## Important APIs, Types, and Functions
`struct pfrt_log_device` stores IDA index, current `struct pfrt_log_info`, parent device, and miscdevice. Important helpers are `get_pfrt_log_data_info()`, `set_pfrt_log_level()`, `get_pfrt_log_level()`, validators for log level/type/revision, `pfrt_log_ioctl()`, `pfrt_log_mmap()`, and probe/remove functions. The UAPI is `PFRT_LOG_IOC_SET_INFO`, `PFRT_LOG_IOC_GET_INFO`, and `PFRT_LOG_IOC_GET_DATA_INFO` from `<uapi/linux/pfrut.h>`.

## Control Flow and State
Probe verifies an ACPI handle and `_DSM`, allocates an ID, initializes revision 1, registers a dynamic miscdevice named `pfrtN` with node `acpi_pfr_telemetryN`, and stores driver data. Ioctls copy UAPI structs, validate revision/level/type, call `_DSM` functions 1, 2, or 3 with typed package results, and copy results back. `mmap()` rejects writable mappings, clears `VM_MAYWRITE`, queries log data, uses chunk2 physical address as base, validates page alignment and mapping size, marks the VMA noncached, and maps it with `io_remap_pfn_range()`.

## State and Persistence
State persists per miscdevice in selected log revision, log type, and cached log level field. Firmware owns the actual telemetry buffer and rollover/reset counters. IDA indices persist for the platform-device lifetime and are freed through devm action.

## Dependencies and Integration Points
The driver depends on ACPI `_DSM` package layouts for the PFRT telemetry GUID, miscdevice/file operations, uaccess, MM remapping, UAPI structs, platform-device ACPI matching, and firmware-provided physical log buffers. It complements `pfr_update.c`, whose update operations create telemetry data.

## Risks and Test Signals
Risks include trusting firmware package buffer sizes after type checks, no explicit serialization across concurrent ioctl/mmap updates to `info`, requiring page-aligned firmware buffer addresses and sizes, using chunk2 as the mmap base, and returning negative log-level errors as a `u32` field to userspace. Test signals are miscdevice creation, `_DSM` status/ext-status debug logs, valid rejection of bad revisions/levels/types, read-only mmap enforcement including `mprotect`, telemetry buffer visibility after a PFRU update, and removal deregistering the miscdevice.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/pfr_telemetry.c -->
