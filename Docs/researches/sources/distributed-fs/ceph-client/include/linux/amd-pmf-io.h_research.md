# sources/distributed-fs/ceph-client/include/linux/amd-pmf-io.h

## Purpose
Defines the interface between AMD Platform Management Framework consumers and PMF/SFH firmware-facing providers for sensor and NPU metric queries.

## Important APIs, Types, And Functions
`enum sfh_message_type` selects HPD, ambient light, or SRA data. `enum sfh_hpd_info` describes human-presence state. `struct amd_sfh_info` carries ambient light, user presence, platform type, and laptop placement. `enum laptop_placement` names placement states such as table, lap motion, in bag, and out of bag. `struct amd_pmf_npu_metrics` reports NPU clock, per-engine busy array, power, MPNPU clock, and read/write bandwidth. Exported functions are `amd_get_sfh_info()` and `amd_pmf_get_npu_data()`.

## Control Flow, State, And Persistence
The header only describes synchronous query calls. Runtime state is supplied by PMF/SFH firmware and copied into caller-provided output structures. No persistence is defined beyond the current sample returned by the PMF driver.

## Dependencies And Integration Points
Depends on `linux/types.h`. Integrates PMF, AMD Sensor Fusion Hub/MP2 firmware, platform profile, presence sensing, ambient-light handling, and NPU telemetry consumers.

## Risks And Test Signals
Risks include stale firmware data, struct layout mismatches across providers, and consumers assuming units or enum values not guaranteed by firmware. Tests should validate NULL/invalid output handling in implementations, unit ranges, HPD state transitions, NPU busy array bounds, and build linkage when PMF providers are modular.
