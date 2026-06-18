# sources/distributed-fs/ceph-client/drivers/tty/hvc/hvcs.c

## Purpose
`hvcs.c` is the IBM Hypervisor Virtual Console Server tty driver. Unlike the generic HVC backends that expose this partition's console, HVCS exposes server-side VIO `serial-server` adapters so userspace can connect to partner partition consoles through `/dev/hvcs*`.

## Important APIs, Types, and Functions
`struct hvcs_struct` stores tty-port state, index, todo mask, a 16-byte output buffer, connection status, partner unit/partition/location fields, VIO device, and destruction completion. Sysfs device attributes expose partner vtys, partner/current location codes, vterm state, and driver-assigned index; driver attribute `rescan` refreshes partner info.

TTY operations are `hvcs_install()`, `hvcs_open()`, `hvcs_close()`, `hvcs_cleanup()`, `hvcs_hangup()`, `hvcs_write()`, `hvcs_write_room()`, `hvcs_chars_in_buffer()`, `hvcs_throttle()`, and `hvcs_unthrottle()`. Device lifecycle is `hvcs_probe()` and `hvcs_remove()`. Core runtime setup is lazy in `hvcs_initialize()`.

## Control Flow
Module init registers a VIO driver for `serial-server`/`hvterm2`. First probe lazily allocates the tty driver, index list, partner-info page buffer, and `khvcsd` thread. Probe assigns the lowest free `/dev/hvcsN` index, allocates `hvcs_struct`, fetches partner info, and adds it to the global list. Install/open connects to the partner via firmware, enables IRQs, requests the IRQ, schedules an initial read, and installs the tty port.

Interrupts disable VIO interrupts, mark read work, and kick `khvcsd`. The worker scans all devices, calls `hvcs_io()`, flushes pending writes via `hvc_put_chars()`, reads up to 16 bytes via `hvc_get_chars()`, pushes tty flip buffers, and re-enables interrupts when drained. Close disables interrupts, clears the tty pointer early, waits for sent data, and frees the IRQ. Remove vhangups attached tty and waits for port destruction.

## State and Persistence Behavior
Global state includes `hvcs_index_list`, `hvcs_index_count`, `hvcs_structs`, `hvcs_task`, `hvcs_pi_buff`, and `hvcs_rescan_status`. Per-device partner and connection state persists while the VIO device exists and can be refreshed by sysfs rescan. No durable state exists.

## Dependencies and Integration Points
HVCS depends on the tty core, VIO bus, PowerPC hypervisor console/server calls (`hvc_get_chars()`, `hvc_put_chars()`, `hvcs_register_connection()`, `hvcs_free_connection()`, partner info helpers), kthreads, sysfs attributes, IRQs, and tty-port reference management.

## Risks and Edge Cases
Partner info is not firmware-notified, so stale partner data requires manual rescan and retry-on-`-EINVAL`. `hvcs_partner_free()` loops while firmware returns `-EBUSY`. The driver must not echo by default because remote console echo could recurse. Index reuse on hotplug is manual and must stay balanced with port destruction. Write-room promises are backed by an internal 16-byte buffer and deferred worker retries.

## Test Signals
Signals include VIO probe/remove, `/dev/hvcsN` lowest-free index reuse, sysfs partner fields, rescan status, busy partner open returning `-EBUSY`, IRQ-driven reads, write buffering and `tty_wait_until_sent()`, throttle/unthrottle interrupt toggling, and clean module unload after active tty hangups.
