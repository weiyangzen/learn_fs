# sources/distributed-fs/ceph-client/net/devlink/health.c

## Purpose

`health.c` implements devlink health reporters and formatted diagnostic messages. Drivers create reporters for devices or ports, report errors, optionally auto-dump diagnostic state, optionally auto-recover, and expose reporter configuration, dumps, diagnosis, recovery, and tests over devlink netlink.

## Important APIs, Types, and Functions

Core types are private `struct devlink_health_reporter`, `struct devlink_fmsg`, and `struct devlink_fmsg_item`. Reporter APIs include `devl_health_reporter_create()`, `devlink_health_reporter_create()`, port variants, destroy functions, `devlink_health_report()`, `devlink_health_reporter_recovery_done()`, `devlink_health_reporter_state_update()`, and `devlink_health_reporter_priv()`. Formatted message APIs include object/pair/array/binary nest helpers, typed put helpers, pair put helpers, `devlink_fmsg_binary_pair_put()`, and `devlink_fmsg_dump_skb()`. Netlink handlers cover reporter get/set, recover, diagnose, dump get, dump clear, and test.

## Control Flow

Reporter creation validates ops defaults, initializes graceful/burst periods, auto-recover, and auto-dump based on available callbacks, and links the reporter into either the device or port list. `devlink_health_report()` logs a trace event, increments error count, marks error state, sends notification, enforces burst/graceful recovery suppression, optionally stores a dump under devlink lock, and optionally invokes recovery. Dump capture allocates an fmsg, opens an object nest, calls driver `dump()`, closes the nest, stores jiffies and real timestamps, and keeps the dump until cleared or replaced. Diagnosis uses a temporary fmsg and streams it immediately. Dump get caches the dump timestamp in dump state to detect concurrent dump replacement.

## State and Persistence Behavior

Each reporter persists counters, health state, auto settings, periods, last recovery timestamp, dump timestamps, and one cached `dump_fmsg`. Fmsg state is an ordered list of typed items plus a sticky first-error field and binary-mode guard. Recovery burst behavior uses jiffies and recovery counts to avoid repeated automatic recovery after recent errors.

## Dependencies and Integration Points

The file integrates with devlink netlink, devlink ports, tracepoints, skb inspection, and driver-provided `devlink_health_reporter_ops` callbacks for recover, dump, diagnose, and test. It uses devlink locking when storing dumps and invoking recovery from automatic paths.

## Risks

Reporter lifetimes depend on drivers destroying reporters before devlink teardown. Auto-recovery suppression is subtle: previous error state, burst period, graceful period, and last recovery timestamp all influence behavior. Fmsg nesting is protocol-sensitive; binary data must be wrapped with the binary pair API, and oversize items set sticky errors. Multipart dump streaming must detect replacement to avoid mixing old and new dumps. Some notification paths assert registration and can warn if called at the wrong lifecycle point.

## Test Signals

Test reporter create/destroy for device and port reporters, duplicate names, get/set auto flags and periods, error report with auto-dump and auto-recover on/off, recovery abort during bursts, manual recover, diagnose output, dump get/clear with multipart output, concurrent dump replacement returning `-EAGAIN`, fmsg binary misuse returning errors, and `devlink_fmsg_dump_skb()` field emission.
