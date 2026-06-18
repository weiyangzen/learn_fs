# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-etm-perf.h

## Purpose

This header defines the shared perf-facing CoreSight ETM contract used by ETM3x, ETM4x, sink drivers, and the CoreSight syscfg layer. It assigns perf event config bitfields, declares filter/session data structures, and exposes helpers for PMU sysfs links and sink configuration lookup.

## Important APIs, Types, and Constants

- `ETM_ADDR_CMP_MAX` sets the perf filter limit to 8.
- `ATTR_CFG_FLD_*` macros define perf `config`, `config2`, and `config3` bit layouts for preset, timestamp, branch broadcast, cycle accuracy, context ID tracing, deprecated timestamp, return stack, sink ID, config ID, and cycle count threshold.
- `struct etm_filter` stores one range, start, or stop filter.
- `struct etm_filters` stores up to `ETM_ADDR_CMP_MAX` filters plus `nr_filters` and `ssstatus`.
- `struct etm_event_data` stores per-event CoreSight state: deferred cleanup work, CPU mask, AUX hardware-ID emission mask, sink buffer config, active syscfg hash, and a percpu path array.
- `etm_perf_sink_config()` extracts sink-private buffer configuration from a perf AUX handle.

## Control Flow and Integration

Perf event format definitions in this header are consumed by `coresight-etm-perf.c` to generate sysfs PMU format files and by ETM3x/ETM4x event parsers through `ATTR_CFG_GET_FLD()`. The filter structures are allocated and populated by the perf layer, then generation-specific source drivers consume them to program ETM address comparators.

## State and Persistence

The header defines in-memory session state only; there is no persistent storage. `struct etm_event_data` lifetime is controlled by perf AUX setup/free and deferred work. `ssstatus` persists across task schedule-out within a perf event so ETM4 start/stop tracing can resume correctly.

## Dependencies, Risks, and Test Signals

It depends on Linux percpu definitions, perf AUX handle types, CoreSight private address type definitions, CoreSight devices, and syscfg descriptors. The perf bit layout is an ABI surface exposed through PMU sysfs format files, so changes must preserve compatibility, including the deprecated timestamp bit. Test signals include PMU format file contents, sink/config selection through `config2`, timestamp via both current and deprecated positions, and start/stop filter rescheduling behavior.
