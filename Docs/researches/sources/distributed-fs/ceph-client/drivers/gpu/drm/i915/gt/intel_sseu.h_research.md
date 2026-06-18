# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_sseu.h

## Purpose
`intel_sseu.h` defines the topology data model and API for i915 slice/subslice/EU and Xe_HP DSS discovery, reporting, and powergating requests.

## Important APIs, Types, And Functions
Important definitions include maximum slice/subslice/EU constants, `intel_sseu_ss_mask_t`, `struct sseu_dev_info`, and `struct intel_sseu`. Inline helpers include `intel_sseu_from_device_info()`, `intel_sseu_has_subslice()`, and `intel_sseu_find_first_xehp_dss()`. It declares topology init, mask copy, RPCS generation, dump/print, and slice-mask conversion functions.

## Control Flow
The header has inline query/conversion logic only. Runtime flow is implemented in `intel_sseu.c`, which fills the declared structures and uses the inline helpers to abstract HSW-style masks versus Xe_HP bitmaps.

## State, Persistence, And Dependencies
`sseu_dev_info` persists in GT info and captures available hardware topology; `intel_sseu` is a per-context/engine powergating request. Dependencies include Linux bitmaps, kernel helpers, GEM warning macros, and DRM/i915 forward declarations.

## Integration Points
GT init, query UAPI, perf, context state, RPCS programming, debugfs, and topology dumps all include this header.

## Risks
The unioned HSW and Xe_HP mask representations require callers to branch on `has_xehp_dss`. `intel_sseu_from_device_info()` uses HSW fields and is not a general Xe_HP conversion. UAPI stride constants must match userspace expectations.

## Test Signals
Builds across platforms, topology query ABI tests, bitmap boundary tests up to `I915_MAX_SS_FUSE_BITS`, and RPCS generation tests validate the contract.
