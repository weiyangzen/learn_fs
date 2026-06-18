# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_vsec.h

## Purpose

`xe_vsec.h` declares Xe VSEC initialization and PMT telemetry read callbacks.

## Important APIs, Types, and Functions

The header declares `xe_vsec_init(struct xe_device *xe)` and `xe_pmt_telem_read(struct device *dev, u32 guid, u64 *data, loff_t user_offset, u32 count)`. It forward-declares `struct device` and `struct xe_device` and includes Linux types for fixed-width and `loff_t` use.

## Control Flow and State

The header contains no state. The implementation registers intel_vsec auxiliary interfaces during device initialization and serves telemetry reads through the PMT callback.

## Dependencies and Integration Points

It forms the interface between Xe device probe code and the VSEC/PMT implementation. `xe_pmt_telem_read()` is also referenced by the callback table passed to intel_vsec.

## Risks and Edge Cases

The telemetry read prototype must remain compatible with the `pmt_callbacks` contract. Future VSEC support should avoid exposing platform-specific data structures through this small header unless multiple modules need them.

## Test Signals

Build coverage validates prototype compatibility. Runtime coverage belongs to VSEC registration and telemetry read tests in `xe_vsec.c`.
