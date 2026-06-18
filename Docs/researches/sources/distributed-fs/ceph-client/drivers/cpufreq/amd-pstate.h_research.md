# sources/distributed-fs/ceph-client/drivers/cpufreq/amd-pstate.h

## Purpose

This header defines the shared private interface for AMD P-State implementation and its unit tests. It describes cached CPPC performance fields, APERF/MPERF sampling data, per-CPU AMD pstate driver data, mode values, and exported helper prototypes.

## Important APIs, types, and functions

`union perf_cached` packs CPPC performance capabilities and computed min/max limits into a u64-friendly cache. `struct amd_aperf_mperf` stores APERF, MPERF, and TSC samples. `struct amd_cpudata` is the central per-policy object: CPU id, QoS requests, CPPC request caches, perf cache, prefcore ranking, floor performance metadata, frequency limits, APERF/MPERF samples, boost/prefcore flags, EPP policy state, suspend state, power notifier, and platform-profile device state. `enum amd_pstate_mode` defines undefined, disable, passive, active, guided, and max sentinel modes.

## Control flow, state, and persistence

The header has no executable control flow. Its state definitions determine what `amd-pstate.c` allocates during policy init and what `amd-pstate-ut.c` inspects during tests. Fields such as `bios_min_perf`, `bios_floor_perf`, `cppc_req_cached`, and `cppc_req2_cached` are especially important for restoring firmware defaults and preserving sane state across hotplug, suspend, and kexec.

## Dependencies and integration points

The header depends on PM QoS and platform-profile definitions and forward-declares cpufreq/sysfs types where possible. It exposes `amd_pstate_get_status()`, `amd_pstate_update_status()`, EPP show/store helpers, `amd_pstate_clear_dynamic_epp()`, and `amd_pstate_get_current_attrs()` for the test module and other AMD pstate-adjacent code.

## Risks and test signals

Because this header exposes private structures outside the main driver, layout or semantic changes must be coordinated with `amd-pstate-ut.c`. Risks include stale comments, tests relying on fields that production code no longer maintains, and cache fields being read without appropriate synchronization. Test signals are successful AMD pstate build, module-test access to `struct amd_cpudata`, and no mismatch between documented perf ordering and runtime checks.
