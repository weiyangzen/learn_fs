<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_eu_stall.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_eu_stall.h

## Purpose
`xe_eu_stall.h` declares the EU stall observation API and the platform support predicate.

## Important APIs, types, and functions
The header declares `xe_eu_stall_get_per_xecore_buf_size()`, `xe_eu_stall_data_record_size()`, `xe_eu_stall_get_sampling_rates()`, `xe_eu_stall_init()`, and `xe_eu_stall_stream_open()`. Inline `xe_eu_stall_supported_on_platform()` returns true for non-SRIOV-VF PVC or graphics version 20 and newer.

## Control flow and integration points
Callers use the support predicate before initializing GT state or exposing observation stream open behavior. The open function is invoked from the observation ioctl path and returns an anonymous fd for stream operations.

## State and persistence behavior
The header owns no state. The implementation allocates `gt->eu_stall`, stream objects, pinned BOs, workqueues, runtime PM references, and forcewake references.

## Dependencies, risks, and test signals
Dependencies are GT/device types and SR-IOV mode helpers. Risks are platform predicate drift, missing declarations for observation integration, and exposing the feature on VF where registers are unavailable. Test signals are platform capability queries, build coverage with observation code, SR-IOV VF rejection, and stream open tests on PVC/Xe2+ hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_eu_stall.h -->
