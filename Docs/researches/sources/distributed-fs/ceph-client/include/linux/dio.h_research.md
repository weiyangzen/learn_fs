<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dio.h -->
# sources/distributed-fs/ceph-client/include/linux/dio.h

## Purpose
Declares the HP300 DIO/DIO-II bus model, device IDs, resource helpers, and driver registration API.

## Important APIs, Types, And Functions
Key types are `dio_id`, `struct dio_dev`, `struct dio_bus`, `struct dio_device_id`, and `struct dio_driver`. APIs include `dio_find()`, `dio_scodetophysaddr()`, `dio_create_sysfs_dev_files()`, `dio_register_driver()`, `dio_unregister_driver()`, `dio_get_drvdata()`, and `dio_set_drvdata()`. Macros encode select-code address ranges, register offsets, primary/secondary IDs, resource helpers, and memory-region request/release.

## Control Flow
The DIO core scans select codes, reads ID/IPL registers from mapped DIO address space, creates `dio_dev` objects, matches drivers by ID table or wildcard, and calls probe/remove through the driver model. Drivers claim the memory resource with `dio_request_device()` and release it on teardown.

## State And Persistence
State is per-bus and per-device kernel state: the single `dio_bus`, device lists, resource windows, select code, encoded ID, interrupt priority, name, and memory resource. No durable state is maintained.

## Dependencies And Integration Points
Depends on HP300 architecture definitions, 8-bit I/O accessors, resources, and the Linux driver model. It integrates legacy HP DIO serial, LAN, HP-IB, SCSI, framebuffer, VME, and miscellaneous board drivers.

## Risks And Edge Cases
DIO-II support is only partially described; comments note the address space is too large to map fully. Secondary IDs matter mainly for framebuffers and must be encoded consistently. Select-code holes, HP320 maximum select code, and resource lengths differ between DIO and DIO-II. Incorrect `in_8()` base handling can misidentify hardware.

## Test Signals
Build HP300 configurations, validate scan results for known ID tables, resource start/end/length calculations, secondary framebuffer IDs, driver probe/remove, sysfs files, and memory-region conflict handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dio.h -->
