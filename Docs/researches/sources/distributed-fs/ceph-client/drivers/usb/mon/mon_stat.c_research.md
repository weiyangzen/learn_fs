# sources/distributed-fs/ceph-client/drivers/usb/mon/mon_stat.c

## Purpose

`mon_stat.c` implements usbmon's lightweight debugfs statistics reader, the `Ns` files under `/sys/kernel/debug/usbmon`, for inspecting usbmon reader and event counters.

## Important APIs, Types, and Functions

`struct snap` stores one formatted snapshot string. `mon_stat_open()` allocates the snapshot and formats `nreaders`, `cnt_events`, and `cnt_text_lost` from the `mon_bus` in `inode->i_private`. `mon_stat_read()` uses `simple_read_from_buffer()`, and `mon_stat_release()` frees the snapshot. `mon_fops_stat` is exported to `mon_text.c` for debugfs file creation.

## Control Flow

Opening the stat file captures one point-in-time line. Reads return that fixed line according to the file offset. Closing releases the allocated snapshot. The code intentionally does not update while the file is held open.

## State and Persistence Behavior

The stat file maintains only the per-open snapshot buffer. Source counters live in `struct mon_bus`; this file does not mutate them. The source comment notes that it reads through locks, so access is intended for protected debugfs use.

## Dependencies and Integration Points

It depends on debugfs files created by `mon_text_add()`, `mon_bus` fields from `usb_mon.h`, and standard file/user-copy helpers. It is part of the text/debugfs usbmon interface rather than the binary char device.

## Risks and Test Signals

Risks are stale snapshots and unlocked counter reads racing with event updates, acceptable for diagnostics. Test signals include `cat /sys/kernel/debug/usbmon/0s`, reader counts changing after opening text or binary captures, event counts increasing after USB traffic, and `text_lost` increasing when text readers overflow.
