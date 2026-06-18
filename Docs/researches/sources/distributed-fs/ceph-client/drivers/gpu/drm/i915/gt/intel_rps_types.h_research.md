# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_rps_types.h

## Purpose
`intel_rps_types.h` defines the data structures behind i915 RPS and Gen5 IPS power accounting.

## Important APIs, Types, And Functions
Key types are `struct intel_ips`, `struct intel_rps_ei`, `struct intel_rps_freq_caps`, and `struct intel_rps`. `intel_rps` stores synchronization, timer/work, PM interrupt state, hardware and software frequency limits, boost and waiter counters, power-mode thresholds, and manual residency samples.

## Control Flow
The fields are initialized in early and platform init, updated by enable/park/unpark paths, modified by interrupt or timer work, and read by sysfs/debugfs/display/IPS integrations. `intel_rps_freq_caps` is populated by hardware cap readers before deriving limits.

## State, Persistence, And Dependencies
All fields are volatile kernel driver state, not disk persistence. Frequency fields are platform-encoded hardware units, not always MHz. Dependencies include atomics, mutexes, timers, ktime, and workqueues.

## Integration Points
`struct intel_gt` embeds `struct intel_rps`; GT PM, GuC SLPC, request waitboost, display RPS, debug dumps, and IPS callbacks all observe or mutate it.

## Risks
The unit distinction for frequency fields is easy to misuse. `flags` and `pm_iir` have separate lock domains from `power` fields. Gen5 IPS data is protected by an external spinlock, not the RPS mutex.

## Test Signals
Lockdep, KCSAN-style race checks, RPS selftests, and platform frequency conversion tests help validate this type’s invariants.
