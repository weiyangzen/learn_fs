
# sources/distributed-fs/ceph-client/arch/powerpc/perf/hv-common.c

## Purpose

This file implements shared hypervisor perf capability discovery for PowerPC hypervisor PMUs.

## Important APIs, Types, And Functions

- `hv_perf_caps_get(struct hv_perf_caps *caps)` issues `H_GET_PERF_COUNTER_INFO` for `HV_GPCI_system_performance_capabilities`, decodes the returned version and capability bits, and fills `struct hv_perf_caps`.

## Control Flow

The function builds an aligned packed parameter/result structure, initializes request type and starting index, calls `plpar_hcall_norets()`, returns the hcall error if nonzero, and otherwise decodes `perf_collect_privileged` plus GA/expanded/LAB capability-mask bits.

## State And Persistence

No persistent local state. It writes the caller-provided `hv_perf_caps` and reads hypervisor state on each call.

## Dependencies And Integration Points

It depends on `H_GET_PERF_COUNTER_INFO`, `hv-gpci.h` request/response structures, physical address conversion, endian helpers, and the shared header `hv-common.h`. It is used by `hv-24x7.c` and other hypervisor perf drivers.

## Risks And Edge Cases

The hcall argument structure must remain correctly packed and aligned to `uint64_t`. Capability interpretation must match the hypervisor GPCI ABI. Callers must handle nonzero hcall returns.

## Test Signals

Test on LPAR systems with different hypervisor capability masks, hcall failure paths, and consumers that require privileged collection.
