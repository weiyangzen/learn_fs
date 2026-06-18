# sources/distributed-fs/ceph-client/drivers/input/rmi4/rmi_f54.c

## Purpose

`rmi_f54.c` implements RMI4 Function 54 diagnostics as a V4L2 touch video device. It exposes sensor image reports such as normalized delta images, raw capacitance, baseline, and full raw reports through videobuf2 capture/read/mmap interfaces.

## Important APIs, Types, and Functions

`enum rmi_f54_report_type` lists supported report IDs. `struct f54_data` stores sensor geometry, capabilities, report buffers, busy/completion state, delayed work, V4L2 objects, vb2 queue, and input/report map. Important functions include `is_f54_report_type_valid()`, `rmi_f54_create_input_map()`, `rmi_f54_request_report()`, `rmi_f54_get_report_size()`, `rmi_f54_buffer_queue()`, `rmi_f54_work()`, V4L2 ioctl handlers, `rmi_f54_detect()`, `rmi_f54_probe()`, and `rmi_f54_remove()`.

## Control Flow

Probe reads F54 query properties, allocates a maximum u16 report buffer, creates a workqueue, builds the V4L2 input map, selects the first valid input, registers a V4L2 device, initializes a vmalloc vb2 queue, and registers a touch video device. Config clears the F54 IRQ bit because the driver polls command completion. Queueing a vb2 buffer requests a report, waits for the delayed work to complete it, copies report data into the buffer, and marks the buffer done or error. The work item polls the command register until `GET_REPORT` clears, then reads report data from the FIFO in 32-byte chunks.

## State and Persistence Behavior

The driver persists selected report type, V4L2 input/format, report buffer, sequence number, busy flag, timeout, and workqueue. Hardware state changes include writing report type, issuing `GET_REPORT`, setting FIFO offsets, and disabling F54 interrupts. Report data persists in memory until overwritten by the next capture.

## Dependencies and Integration Points

The file depends on RMI transport reads/writes, V4L2 core, videobuf2 vmalloc memory ops, Linux media touch pixel formats, workqueues, completions, and electrode counts from F55 via `rmi_driver_data` when available.

## Risks and Edge Cases

The polling path must avoid leaving `is_busy` stuck after errors. `rmi_f54_set_input()` uses u16-sized `bytesperline` and `sizeimage` for all formats, while 8-bit reports have a smaller actual payload. Report data is read in 32-byte chunks for SMBus compatibility. Workqueue removal destroys the queue but does not explicitly cancel delayed work on the normal remove path before destroy. Concurrent V4L2 input changes and queued buffers rely on the queue lock/status mutex behavior.

## Test Signals

Tests should cover V4L2 enumeration, each supported report type, 8-bit and 16-bit payload sizes, buffer queue/read/mmap/poll paths, command timeout injection, FIFO chunk reads over SMBus, electrode count override from F55, stream stop sequence reset, remove while idle and while work is pending, and media-device userspace tools such as `v4l2-ctl`.
