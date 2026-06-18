# sources/distributed-fs/ceph-client/drivers/usb/misc/usbtest.c

## Purpose
`usbtest.c` is a USB core and host-controller test driver. It binds known USB test/gadget devices or a module-parameter-selected generic device, then exposes an ioctl through usbfs to run numbered tests for control, bulk, interrupt, isochronous, scatter-gather, unlink, halt, toggle, DMA mapping, and unaligned-buffer behavior.

## Important APIs, Types, and Functions
`struct usbtest_info` describes endpoint expectations and supported test classes for a device. `struct usbtest_dev` stores the interface, selected pipes, endpoint descriptors, per-device mutex, and scratch buffer. User ABI structs are `usbtest_param_32` and compat `usbtest_param_64`, both used with `_IOWR('U', 100, ...)`.

Endpoint setup is handled by `get_endpoints`. URB helpers include `usbtest_alloc_urb`, `simple_alloc_urb`, `complicated_alloc_urb`, `simple_fill_buf`, `simple_check_buf`, `simple_io`, and `simple_free_urb`. Scatter-gather helpers are `alloc_sglist`, `perform_sglist`, and timer cancellation support. Control tests are implemented by `ch9_postconfig` and `test_ctrl_queue`. Unlink/halt/toggle tests use `unlink1`, `unlink_queued`, `halt_simple`, and `toggle_sync_simple`. Isochronous and queued transfer tests use `iso_alloc_urb`, `test_queue`, and `complicated_callback`.

## Control Flow
`usbtest_probe` optionally matches generic module parameters, allocates device state and scratch buffer, selects endpoints either from fixed endpoint numbers or descriptor autoconfiguration, stores interface data, and logs available test channels. `usbtest_ioctl` locks the per-device mutex, resets the preferred altsetting, translates 64-bit compat parameters to the 32-bit internal form when needed, records start time, calls `usbtest_do_ioctl`, and writes duration back on success.

`usbtest_do_ioctl` validates iterations and scatterlist depth and dispatches test numbers 0 through 29. Tests cover simple bulk reads/writes, variable-length bulk I/O, scatter-gather bulk I/O, USB chapter 9 descriptor/status sanity checks, queued control URBs with expected stalls/short reads, unlink behavior for single and queued URBs, endpoint halt set/clear, vendor control-out loopback, isochronous queues, odd-address DMA/core-map transfers, interrupt transfers, performance-oriented queued bulk, and data-toggle reset via clear-halt.

## State and Persistence
The driver keeps no persistent test results. Runtime state includes selected altsetting, module parameters (`alt`, `pattern`, `realworld`, `force_interrupt`, `vendor`, `product`), endpoint pipe selections, and scratch buffers. Each ioctl fills duration fields for that invocation. Test data patterns are deterministic zeros or mod-63 bytes.

## Dependencies and Integration Points
The file depends on usbcore URB/control/scatter-gather APIs, usbfs driver ioctl plumbing, timers, completions, spinlocks, mutexes, descriptor parsing helpers, and known USB gadget/test firmware behavior. It integrates with devices such as EZ-USB, dedicated USB test firmware, Gadget Zero, user-mode test drivers, and generic module-parameter-selected devices.

## Risks and Edge Cases
This is intentionally a stress and conformance test driver, so many tests can stall endpoints, consume bandwidth, or block for long periods. A source comment warns that usbfs locking can delay disconnect handling while an ioctl runs; aborting tests may require killing the userspace task. Some tests assume cooperative firmware, especially control-out loopback, isochronous source/sink, and bulk data patterns. Scatter-gather reads currently do not verify returned data. Isochronous tests tolerate up to a 10% packet error rate, so failures below that threshold are not fatal. Queued control tests intentionally allow some device-specific stalls when `realworld` mode is enabled. Test parameters can allocate many URBs and buffers up to `MAX_SGLEN`, so memory pressure is part of the risk profile.

## Test Signals
The file is itself a test harness. Useful signals are successful probe endpoint selection, ioctl return codes per numbered test, duration fields being populated, expected `-EOPNOTSUPP` when a requested endpoint class is unavailable, logs for descriptor validation failures, URB timeout/unlink statuses, guard-byte validation for unaligned buffers, lockdep behavior around per-device mutexing, and disconnect/suspend behavior while long-running tests are active.
