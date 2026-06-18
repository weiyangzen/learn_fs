# sources/distributed-fs/ceph-client/include/uapi/linux/tc_act/tc_gate.h

## Purpose
Defines the TC gate action ABI for time-aware gate schedules, commonly used with TSN-like traffic shaping.

## Important APIs, Types, and Constants
`struct tc_gate` embeds `tc_gen`. Nested entry attributes include index, gate state, interval, internal priority value, and max octets. Action attributes include priority, entry list, base time, cycle time, cycle time extension, flags, and clock id.

## Control Flow, State, and Persistence
Userspace installs a schedule. Runtime packet handling checks the selected clock and current schedule entry to allow or gate traffic. Schedule state persists in the action instance.

## Dependencies and Integration Points
Depends on `<linux/pkt_cls.h>`. Integrates with TC, qdisc scheduling, and time-aware networking features.

## Risks and Test Signals
Risks include wrong clock id, schedule wrap errors, invalid intervals, and hardware offload mismatch. Test schedule parsing, base-time alignment, cycle rollover, max-octets limits, and dump/offload behavior.
