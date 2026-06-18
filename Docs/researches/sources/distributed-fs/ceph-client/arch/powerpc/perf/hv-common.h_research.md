
# sources/distributed-fs/ceph-client/arch/powerpc/perf/hv-common.h

## Purpose

This header provides shared types and macros for PowerPC hypervisor perf drivers.

## Important APIs, Types, And Functions

- `struct hv_perf_caps` stores the hypervisor perf counter info version and bitfields for privileged collection, GA, expanded, and LAB capabilities.
- `hv_perf_caps_get()` is declared for shared capability discovery.
- `EVENT_DEFINE_RANGE_FORMAT()` creates a perf PMU format attribute plus helper functions for extracting a bit range from an event attr field.
- `EVENT_DEFINE_RANGE_FORMAT_LITE()` creates only the format attribute.
- `EVENT_DEFINE_RANGE()` generates `event_get_<name>_max()` and `event_get_<name>()` helpers.

## Control Flow

The macros expand at compile time into sysfs format attributes and static inline-like helper functions used by hypervisor PMU drivers to parse `perf_event_attr` bit fields.

## State And Persistence

No runtime state is stored by the header. Generated helper functions are pure readers of `event->attr`.

## Dependencies And Integration Points

It depends on Linux perf PMU format attribute macros and fixed-width types. `hv-24x7.c` uses it for domain/index/offset/lpar fields; GPCI-related drivers use the capability type and range macros.

## Risks And Edge Cases

The max helper uses shift arithmetic and includes a `BUILD_BUG_ON()` for invalid bit ranges. Macro-generated function names can collide if the same range name is reused in one translation unit. `EVENT_DEFINE_RANGE_FORMAT_LITE()` intentionally omits helper functions to avoid unused warnings.

## Test Signals

Build warnings/errors from macro use, sysfs `format/` files, and event parsing tests for boundary values in each configured bit range are useful signals.
