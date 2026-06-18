# sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_ec_chardev.c

Purpose: misc character device for userspace access to ChromeOS EC commands, legacy version text, direct EC memory reads, and queued MKBP events.

Important APIs, types, and functions: `struct chardev_priv` stores per-open EC pointer, notifier, waitqueue, event mask, event list, queued length, and command offset. `ec_get_version()` implements legacy read output. `cros_ec_chardev_mkbp_event()` enqueues selected events from the EC notifier chain. File operations implement open, poll, read, release, and ioctls `CROS_EC_DEV_IOCXCMD`, `CROS_EC_DEV_IOCRDMEM`, and `CROS_EC_DEV_IOCEVENTMASK`.

Control flow: probe registers a miscdevice named from platform data (`cros_ec` or `cros_pd`). Open allocates per-file state and registers a notifier on `ec_dev->event_notifier`. If the user sets an event mask, read blocks or returns queued event records containing one event-type byte plus payload. Without an event mask, read returns EC version strings once. Ioctl command copies a bounded `struct cros_ec_command` from userspace, applies command offset, calls `cros_ec_cmd_xfer()`, and copies response back. Release unregisters notifier and frees queued events.

State and persistence: event queue is per file descriptor and bounded by `CROS_MAX_EVENT_LEN` (`PAGE_SIZE`). `event_mask` selects event types. No persistent hardware state except commands userspace sends.

Dependencies and integration points: depends on `cros-ec-dev` platform devices, miscdevice, notifier chain, poll/waitqueue, userspace ABI headers in `linux/platform_data/cros_ec_chardev.h`, and EC protocol helpers.

Risks and edge cases: event bit calculation uses `1 << event_type`; large event types can overflow `unsigned long` semantics. `copy_to_user(buffer, &event->event_type, count)` relies on event_type and flexible data being contiguous. Event drops are silent when queue limit is exceeded. Ioctl command sizes are bounded by `EC_MAX_MSG_BYTES` but still trust userspace-provided header consistency.

Test signals: userspace `ioctl` command round trips, readmem on LPC-supported devices, event mask filtering and poll behavior, nonblocking reads, queue overflow/drop behavior, compat ioctl, and separate EC/PD command offsets.
