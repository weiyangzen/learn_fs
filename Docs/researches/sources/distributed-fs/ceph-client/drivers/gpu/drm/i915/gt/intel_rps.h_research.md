# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_rps.h

## Purpose
`intel_rps.h` declares the RPS lifecycle, frequency-control, IRQ, boost, dump, and display-integration APIs for GT power management.

## Important APIs, Types, And Functions
It exposes initialization and registration functions, enable/disable, park/unpark, waitboost APIs, frequency conversion helpers, getters/setters for requested/actual/min/max/boost/RP0/RP1/RPn frequencies, threshold accessors, unslice raise/lower controls, throttle/MMIO helpers, IRQ handlers, and `gen6_rps_frequency_dump()`. Inline flag helpers manipulate `INTEL_RPS_ENABLED`, `ACTIVE`, `INTERRUPTS`, and `TIMER`.

## Control Flow
Callers initialize `struct intel_rps`, initialize platform caps, enable during GT power setup, transition active state on GT unpark/park, and use setters/getters from sysfs/debug and request wait paths. IRQ handlers route PM events into worker processing.

## State, Persistence, And Dependencies
The header depends on `intel_rps_types.h`, register definitions, `struct i915_request`, and `struct drm_printer`. It does not store state itself; it defines the API contract for the state in `struct intel_rps`.

## Integration Points
GT PM, request scheduling, display RPS, debugfs/sysfs, GuC SLPC, and legacy IPS module callbacks include this API.

## Risks
Many functions expect caller-side locking or active runtime PM conditions, especially setters and MMIO readers. Inline flag operations are low-level and should remain consistent with enable/park state transitions.

## Test Signals
Compile coverage across SLPC and non-SLPC configs, RPS selftests, sysfs frequency-limit tests, display boost paths, and IRQ handler tests are the main signals.
