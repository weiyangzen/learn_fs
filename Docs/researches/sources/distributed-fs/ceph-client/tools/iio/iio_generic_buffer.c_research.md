# sources/distributed-fs/ceph-client/tools/iio/iio_generic_buffer.c

## Purpose

`iio_generic_buffer.c` captures buffered samples from an IIO device, converts raw scan data using channel metadata, and prints values in scaled units. It is both an example program and a diagnostic tool for triggers, buffers, and channel layout.

## Important APIs and Functions

The program uses IIO buffer UAPI `IIO_BUFFER_GET_FD_IOCTL` and shared helpers from `iio_utils`. `size_from_channelarray` computes aligned scan size and per-channel byte locations. `print1byte`, `print2byte`, `print4byte`, and `print8byte` handle endian conversion, shifts, masks, signed extension, offset, and scale. `process_scan` dispatches per-channel printing. `enable_disable_all_channels` writes `*_en` scan-element attributes. `cleanup` disconnects triggers, disables buffers, and disables auto-enabled channels. Signal handlers call cleanup on interrupt, termination, and abort. `main` parses device, trigger, buffer, loop count, length, eventless, triggerless, and auto-channel options.

## Control Flow and State

After option parsing, the tool resolves a device by name or number, resolves or constructs a trigger unless triggerless mode is selected, builds the enabled channel array, optionally auto-enables channels and rebuilds metadata, constructs a buffer directory, sets `trigger/current_trigger`, opens `/dev/iio:deviceN`, obtains the indexed buffer fd through ioctl, writes buffer length, enables the buffer, computes scan size, allocates a read buffer, and loops polling or sleeping before reading and printing scans. Global variables track configured resources so `cleanup` can undo state at normal exit and on signals.

## Dependencies and Integration

It depends on IIO sysfs, IIO character devices, scan element metadata, optional triggers, and `iio_utils.c`. It integrates with drivers that expose buffer directories and scan elements, and it demonstrates the newer buffer-fd ioctl flow.

## Risks and Test Signals

Sysfs writes mutate live device state, so cleanup correctness matters. The code guards against `scan_size * buf_len` overflow, but many allocations and sysfs reads can fail after partial configuration. Channel formats outside 1, 2, 4, or 8 bytes are silently skipped. Tests should cover named and numeric device/trigger selection, triggerless and eventless modes, auto-channel modes, cleanup after errors and signals, endian/sign extension conversion, multiple buffer indexes, and devices without enabled channels.
