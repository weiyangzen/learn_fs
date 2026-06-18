# sources/distributed-fs/ceph-client/drivers/comedi/drivers.c

## Purpose

This file is central COMEDI driver-management and low-level-driver support code. It owns the registered `comedi_driver` list, manual and automatic attachment flows, post-configuration normalization of subdevices, detach cleanup, helper allocation APIs, DIO/readback helpers, async scan accounting, event handling, firmware loading, legacy I/O-region helpers, and driver unregister cleanup.

## Important APIs, types, and functions

Important exported APIs include `comedi_set_hw_dev()`, `comedi_alloc_devpriv()`, `comedi_alloc_subdevices()`, `comedi_alloc_subdev_readback()`, `comedi_readback_insn_read()`, `comedi_timeout()`, `comedi_dio_insn_config()`, `comedi_dio_update_state()`, `comedi_bytes_per_scan_cmd()`, `comedi_bytes_per_scan()`, `comedi_nscans_left()`, `comedi_nsamples_left()`, `comedi_inc_scan_progress()`, `comedi_handle_events()`, `comedi_load_firmware()`, `__comedi_check_request_region()`, `comedi_check_request_region()`, `comedi_legacy_detach()`, `comedi_auto_config()`, `comedi_auto_unconfig()`, `comedi_driver_register()`, and `comedi_driver_unregister()`. Internal pieces include `comedi_device_detach_cleanup()`, `comedi_device_attach()`, `__comedi_device_postconfig()`, `__comedi_device_postconfig_async()`, `insn_rw_emulate_bits()`, and `comedi_recognize()`.

## Control Flow

Manual configuration enters `comedi_device_attach()` under `dev->mutex`, searches the global driver list under `comedi_drivers_list_lock`, recognizes board names through a driver board table, calls the selected driver's `attach`, then runs `comedi_device_postconfig()`. Auto-configured bus drivers call `comedi_auto_config()`, which allocates a COMEDI minor for the hardware device, sets driver and board name, invokes `auto_attach`, and runs the same postconfig path. Postconfig fills missing device and subdevice callbacks with invalid defaults, initializes DO `io_bits`, allocates async state and buffers for command-capable subdevices, assigns range tables, emulates one-channel read/write through `insn_bits` when possible, and marks the device attached under `attach_lock`.

Detach runs through `comedi_device_detach()` or unregister scanning. It cancels all activity, clears `attached`, increments `detach_count`, calls the low-level `detach`, and frees subdevice private data, minors, async buffers, readback arrays, device-private storage, pacer data, I/O/MMIO/IRQ bookkeeping, callback pointers, and the hardware-device reference. Async helpers compute scan lengths, remaining scans or samples, update scan progress and end-of-scan events, call low-level cancel on terminal events, and forward events to `_comedi_event()`.

## State and Persistence

Persistent storage is not used. Kernel runtime state includes the global `comedi_drivers` linked list, each `struct comedi_device`'s hardware reference, subdevice array, private data, async buffers, state/readback arrays, attachment flags, and counters such as `scans_done`, `scan_progress`, and `detach_count`. State is protected by `comedi_drivers_list_lock`, `dev->mutex`, `dev->attach_lock`, subdevice spin locks, and running-subdevice references. I/O regions, firmware contents, IRQs, and class-device minors are external resources managed by helper calls and cleanup paths.

## Dependencies and Integration Points

This file integrates with the COMEDI internal device/minor, buffer, async-event, and ioctl layers, Linux module references, firmware loading, I/O-port resource management, IRQ cleanup, DMA direction metadata, and low-level drivers on PCI, USB, PCMCIA, ISA, and other buses. Bus helper modules call `comedi_auto_config()` and `comedi_auto_unconfig()`; low-level drivers rely on its subdevice allocation, DIO, timeout, and readback helpers.

## Risks

The highest-risk areas are attach/detach locking, module reference lifetime, and async cleanup. Low-level driver attach failures must call detach and drop module references without leaving allocated minors or hardware references. `__comedi_device_postconfig_async()` allocates async structures before buffer allocation; error paths rely on later detach cleanup. DIO helpers only track up to 32 channels in `state` and `io_bits`; larger devices must split subdevices or handle state themselves. `comedi_timeout()` busy-waits for up to `COMEDI_TIMEOUT_MS`, so callbacks must be cheap and must return `-EBUSY` only while progress is plausible.

## Test Signals

Tests should cover manual `comedi_config` attach/detach, bus auto-probe/remove, low-level attach failure cleanup, driver unregister while devices are attached, async command setup and cancellation, scan accounting for finite and continuous commands, DIO input/output/query behavior, readback allocation and reads, firmware callback errors, I/O-region validation failures, and lockdep-clean detach from open devices.
