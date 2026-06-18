
# sources/distributed-fs/ceph-client/arch/powerpc/perf/hv-24x7-catalog.h

## Purpose

This header defines packed structures for the Power hypervisor 24x7 event catalog, including the page-zero catalog header and individual event records used to generate perf sysfs events.

## Important APIs, Types, And Functions

- `struct hv_24x7_catalog_page_0` describes catalog magic, page length, version, timestamp, and offsets/lengths/counts for schema, event, group, and formula sections.
- `HV_24X7_CATALOG_MAGIC` is the ASCII `"24x7"` marker.
- `struct hv_24x7_event_data` describes one variable-length event entry with domain, group record offsets, counter offset, flags, group metadata, event name length, and trailing name/description/long-description data.

## Control Flow

No executable control flow. `hv-24x7.c` reads catalog pages through hcalls, interprets page zero, validates event entries with these layouts, and builds sysfs attributes from the variable-length event fields.

## State And Persistence

No local state. The packed structs describe hypervisor-provided persistent catalog data for the current platform.

## Dependencies And Integration Points

It depends on Linux fixed-width big-endian types and is consumed by `hv-24x7.c`. The field layout must match the external 24x7 catalog format.

## Risks And Edge Cases

Variable-length trailing data requires strict bounds checks. All multibyte fields are big-endian. Comments note uncertainty around catalog version semantics. Mismatches with firmware catalog format can corrupt sysfs event generation or cause skipped events.

## Test Signals

Validate catalog parsing on POWER systems with 24x7 support, malformed/truncated catalog simulation if available, sysfs event/description generation, and endian correctness.
