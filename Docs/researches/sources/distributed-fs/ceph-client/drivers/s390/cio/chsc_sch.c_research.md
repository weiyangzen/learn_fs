# sources/distributed-fs/ceph-client/drivers/s390/cio/chsc_sch.c

## Purpose
This module is the driver for CHSC subchannels and the `/dev/chsc` misc interface. It enables CHSC subchannels, starts asynchronous CHSC requests on available subchannels, exposes multiple CHSC ioctls to userspace tooling, and supports an optional CHSC command to run when the device file closes.

## Important APIs, Types, and Functions
Key state includes CHSC debug logs, `on_close_request`, `on_close_chsc_area`, `on_close_mutex`, `chsc_lock`, and `chsc_ready_for_use`. The CSS driver callbacks are `chsc_subchannel_probe()`, `chsc_subchannel_irq()`, `chsc_subchannel_remove()`, and `chsc_subchannel_shutdown()`. Request handling centers on `chsc_async()`, `chsc_examine_irb()`, `chsc_ioctl_start()`, `chsc_ioctl_start_sync()`, info ioctls for channel paths/control units/subchannels/configuration/component lists/DCAL, and on-close set/remove handling.

## Control Flow
Module init creates CHSC debug logs, registers the CHSC interruption subclass, registers a CSS driver for subchannel type `SUBCHANNEL_TYPE_CHSC`, and registers the misc device. Probe allocates `struct chsc_private`, stores it as driver data, and enables the subchannel. `chsc_async()` scans enabled, idle CHSC subchannels, sets the request key/SID, issues `chsc()`, and either completes synchronously, records an in-progress request for IRQ completion, or retries another subchannel. IRQ completion copies the IRB, updates SCHIB, completes the request, and drops the subchannel device reference. Ioctls allocate page request areas, copy user input, issue synchronous or asynchronous CHSC commands, then copy results back.

## State and Persistence
State is volatile. Only one `/dev/chsc` opener is allowed through `chsc_ready_for_use`. The on-close command persists only while the device file is open and is freed during release or remove. In-flight asynchronous requests are stored in each subchannel's `chsc_private`. Debug data is kept by the s390 debug feature.

## Dependencies and Integration Points
The module depends on CSS driver registration, low-level `chsc()`, CIO subchannel enable/disable/update helpers, CHSC architecture ioctl structures, `copy_from_user()`/`copy_to_user()`, miscdevice infrastructure, CHSC interruption subclass registration, and the s390 debug feature. It bridges privileged userspace CHSC tools to CHSC subchannel hardware.

## Risks and Test Signals
Risk areas include user-provided page-sized CHSC requests, async request lifetime across remove/release, single-open behavior, global on-close state, response-length copies into user structures, and condition-code/IRB interpretation. Test signals include probing/removing CHSC subchannels, concurrent `/dev/chsc` opens returning `-EBUSY`, each ioctl with valid and malformed payloads, async completion and no-request IRQ logs, on-close execution/removal, and teardown while a request is pending.
