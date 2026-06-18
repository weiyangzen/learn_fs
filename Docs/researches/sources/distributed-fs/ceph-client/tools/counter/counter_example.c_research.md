# sources/distributed-fs/ceph-client/tools/counter/counter_example.c

Purpose: Minimal userspace example for the Linux Counter character device API. It watches count values on `/dev/counter0` and prints event data indefinitely.

Important APIs, types, and functions: Static `watches[2]` configures two `struct counter_watch` entries for Count 0 and Count 1, scope count, event index, channel 0. `main()` opens the device, adds watches with `COUNTER_ADD_WATCH_IOCTL`, enables events with `COUNTER_ENABLE_EVENTS_IOCTL`, reads two `struct counter_event` records at a time, and prints timestamps, values, and status strings.

Control flow: Open, add both watches, enable events, then infinite blocking read loop. Any ioctl/read/short-read error exits.

State and persistence: Configures watches and event enablement on the open counter fd. No file persistence.

Dependencies and integration points: Depends on `/dev/counter0` and UAPI `linux/counter.h`. Demonstrates the counter character device event API for driver developers.

Risks: Hardcoded device, event type, component parents, and assumption that reads return exactly two events. It leaks the fd on early ioctl error by process exit only.

Test signals: Run on a counter device supporting index events for two counts, inject events, verify read sizes and status handling.
