# sources/distributed-fs/ceph-client/drivers/nvdimm/nd-core.h

## Purpose
`nd-core.h` is the private libnvdimm core header. It defines internal `struct nvdimm_bus` and `struct nvdimm`, declares global bus state, exposes internal bus/device/region/label/namespace helper prototypes, and provides configuration fallbacks for optional security and claim support.

## Important APIs, Types, And Declarations
The key private types are `struct nvdimm_bus` and `struct nvdimm`. The bus holds provider descriptor, waitqueue, global list link, device, ID, probe/ioctl activity counters, mapping cache list, reconfiguration mutex, and badrange state. The DIMM holds provider data, command mask, device, busy counter, ID, flush hints, security state/ops/work, and firmware ops.

Declarations cover bus initialization, bus walking, ndctl device creation/destruction, async synchronization, device registration, region seed creation, UUID uniqueness, mapping label cleanup, DPA allocation queries, namespace claim attach/detach, namespace sysfs store, safe PFN conversion, and namespace I/O enable/disable.

The inline `nvdimm_security_flags()` calls provider security ops and warns if mutually exclusive security state bits are reported together.

## Control Flow
This header routes cross-file calls rather than executing high-level logic. It establishes which helpers are internal to libnvdimm and which compile to stubs when `CONFIG_NVDIMM_KEYS` or `CONFIG_ND_CLAIM` is disabled. Device and namespace files rely on these declarations to call across module boundaries without exposing all internals publicly.

## State And Persistence Behavior
The structures define volatile kernel state for buses and DIMMs. Security state mirrors persistent or hardware-backed DIMM security properties, but the header itself only stores cached flags and operation pointers. Badrange state records known bad physical ranges for the bus. Mapping cache state supports shared memremap lifetime.

## Dependencies And Integration Points
`nd-core.h` includes public libnvdimm/device/mutex/nd headers and the private `nd.h`. It is included by most implementation files in this subset. It binds together provider callbacks, NVDIMM bus registration, DIMM devices, region creation, namespace labels, BTT/PFN/DAX seeds, and optional security/claim features.

## Risks And Edge Cases
Because this header exposes private structure layouts across files, changes affect many compilation units. Security state validation warns on providers that report incompatible flags but does not repair them. Optional stubs returning `-EOPNOTSUPP` or `-ENXIO` must match callers' expectations; otherwise features may silently disappear under configuration changes.

## Test Signals
Test signals are mainly compile/config based: builds with and without `CONFIG_NVDIMM_KEYS`, `CONFIG_ND_CLAIM`, BTT, PFN, and DAX should validate stub behavior. Runtime tests should watch for security state warnings, bus activity counters, namespace attach/detach behavior, and badrange propagation across files that consume this header.
