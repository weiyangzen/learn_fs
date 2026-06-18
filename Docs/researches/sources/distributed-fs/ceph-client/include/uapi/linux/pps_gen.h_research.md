<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/pps_gen.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/pps_gen.h

Purpose: defines the generator-side PPS ABI for configuring a PPS pulse generator.

Important APIs and types: `struct pps_gen_event` reports the last generator event and sequence number. `PPS_GEN_EVENT_MISSEDPULSE` identifies a missed pulse. `PPS_GEN_SETENABLE`, `PPS_GEN_USESYSTEMCLOCK`, and `PPS_GEN_FETCHEVENT` are the ioctl controls for enabling generation, querying whether the system clock is used, and fetching event state.

Control flow: userspace configures a PPS generator device through ioctls; the kernel driver enables or disables pulse generation, reports clock-source behavior, and records missed-pulse events for later fetch.

State and persistence: generator enablement, clock-source selection, last event type, and event sequence are runtime device state. No persistent configuration is stored by the header.

Dependencies and integration points: depends on Linux types and ioctl encoding. Integrates with PPS generator drivers and time synchronization test setups that need synthetic PPS signals.

Risks and test signals: risks include timing precision, missed-pulse event loss, ioctl pointer compatibility, and ambiguity around system-clock mode. Test enable/disable, event sequence increments, missed-pulse reporting, invalid ioctl arguments, and pulse output timing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/pps_gen.h -->
