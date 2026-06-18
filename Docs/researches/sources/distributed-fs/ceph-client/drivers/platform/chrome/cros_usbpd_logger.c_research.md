<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_usbpd_logger.c -->
# sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_usbpd_logger.c

## Purpose

This platform driver periodically drains Chrome EC USB Power Delivery log entries and prints formatted kernel log messages describing charger, fault, DisplayPort, and video-codec events.

## Important APIs, Types, And Functions

`struct logger_data` stores the platform device, parent `cros_ec_dev`, command buffer, delayed work, and ordered workqueue. `ec_get_log_entry()` sends `EC_CMD_PD_GET_LOG_ENTRY`. `cros_usbpd_print_log_entry()` converts `struct ec_response_pd_log` into `PDLOG` text. `cros_usbpd_log_check()` drains up to `CROS_USBPD_MAX_LOG_ENTRIES` and requeues itself every minute. PM callbacks cancel and restart the delayed work.

## Control Flow

Probe allocates logger state, creates an ordered workqueue, initializes autocanceled delayed work, and schedules the first check. Each work run fetches entries until an error, `PD_EVENT_NO_ENTRY`, or a 30-entry cap, computes wall-clock event time from the EC timestamp delta, prints a formatted line, and schedules the next run.

## State And Persistence

The driver keeps only the reusable EC command buffer and delayed-work schedule. EC PD logs are consumed from EC firmware; printed logs persist only in the kernel log. Suspend cancels pending work and resume schedules a new delayed check.

## Dependencies And Integration Points

It depends on Chrome EC dev parent data, Chrome EC PD log command definitions, `rtc_ktime_to_tm()`, ordered workqueues, and platform device ID `cros-usbpd-logger`.

## Risks

Kernel log output may be noisy on active PD systems. The formatting code uses a fixed 80-byte buffer with append lengths accumulated from `vsnprintf()` return values; truncation is tolerated by the bounded buffer but can make messages incomplete. The reusable command buffer assumes only the ordered workqueue accesses it.

## Test Signals

Test probe scheduling, log draining limits, formatting of all known PD event types, no-entry stop behavior, EC command errors, suspend cancellation, resume requeue, and timestamp conversion correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_usbpd_logger.c -->
