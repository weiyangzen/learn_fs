# sources/distributed-fs/ceph-client/drivers/gpu/drm/panfrost/panfrost_issues.h

## Purpose
This header enumerates hardware issues and errata masks for supported Mali GPU models and revisions.

## Important APIs, Types, and Functions
`enum panfrost_hw_issue` lists driver-relevant errata. `hw_issues_*` macros define common, model, and revision-specific bitmasks. `panfrost_has_hw_issue` tests a device's runtime issue bitmap.

## Control Flow
The only executable logic is the inline bitmap test. GPU feature initialization combines these masks after matching GPU ID/revision, and other subsystems branch on the resulting issue bits.

## State and Persistence Behavior
The header defines static masks. Runtime issue state is stored in `pfdev->features.hw_issues`.

## Dependencies and Integration Points
Issue predicates are consumed by GPU quirk programming, job submission flags, reset policy, MMU workarounds, performance counter behavior, and exception reset decisions.

## Risks
Errata data must match exact GPU revisions. Missing an issue can cause hangs, data corruption, or missing resets; falsely enabling an issue can reduce performance or change programming sequences incorrectly. The list is intentionally incomplete and includes only issues the driver uses.

## Test Signals
Validate boot logs against known GPU revisions, exercise code paths for issue-dependent flags, run conformance workloads on each model, and test fault/reset cases such as TTRX_3076 bus-fault recovery.
