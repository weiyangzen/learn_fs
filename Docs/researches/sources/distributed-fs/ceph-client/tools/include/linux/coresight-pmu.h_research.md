# sources/distributed-fs/ceph-client/tools/include/linux/coresight-pmu.h

## Purpose

This header defines CoreSight ETM PMU names and AUX hardware ID encoding helpers used by perf and related tools.

## APIs, State, and Dependencies

It defines `CORESIGHT_ETM_PMU_NAME`, the legacy CPU-to-trace-ID formula, masks for `PERF_RECORD_AUX_OUTPUT_HW_ID` fields, and helpers to extract trace ID, sink ID, minor version, and major version from packed hardware IDs. It depends on `<linux/bits.h>` and has no state.

## Risks and Test Signals

The field layout is part of the perf/CoreSight userspace contract. Incorrect masks break trace decoding and CPU/sink association. Tests should decode known AUX hardware IDs, including legacy and versioned values, and compare against perf output on CoreSight systems.
