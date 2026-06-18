<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/scheduler/Scheduler.hh -->
# sources/distributed-fs/eos/mgm/scheduler/Scheduler.hh

## Purpose
Declares the MGM scheduler facade used by file creation, replica placement, and file access paths. It defines placement/access argument bundles, placement policies, scheduler modes, and static scheduling entry points.

## Important APIs and Types
- `enum tPlctPolicy { kScattered, kHybrid, kGathered }`: controls locality/collocation of stripes.
- `enum tSchedType { regular, draining }`: distinguishes normal scheduling from draining workflows.
- `PlacementArguments`: input/output carrier for file placement:
  - Inputs include space name, path, group tag, layout id, inode, placement policy, target geotag, truncation flag, forced group index, booking size, scheduler type, optional strategy override, and virtual identity.
  - Outputs/mutable inputs include already-used fsids, selected fsids, excluded fsids, data proxies, and firewall entry points.
  - Builder helpers `setFileParams`, `setFsParams`, and `setPlctParams` reduce call-site argument ordering mistakes.
  - Strong wrapper structs `Path`, `GroupTag`, `Lid`, `BookingSize` plus namespace helpers make typed construction easier.
- `AccessArguments`: input/output carrier for access scheduling:
  - Inputs include forced fsid/space, tried CGI, layout id, inode, RW flag, booking size, scheduler type, virtual identity, file locations, and excluded fsids.
  - Outputs include proxies, firewall entry points, selected layout index, and unavailable fsids.
- Static functions: `FilePlacement`, `FlatSchedulerFilePlacement`, `FileAccess`, `FlatSchedulerFileAccess`, `getRequiredReplicas`, placement policy string conversion, and `ReshuffleFs`.

## Control Flow and Usage Contract
The header documents that `FilePlacement` and `FileAccess` must be called with `FsView::gFsView::ViewMutex` locked. `isValid()` methods provide precondition checks but are not enforced automatically by the implementations. Layout validity for placement includes a replica count guard: `GetStripeNumber(lid) + 1` must fit below `std::numeric_limits<uint8_t>::max()`.

## State and Persistence
The class itself is a static facade. It declares process-local state `pMapMutex` and `schedulingGroup` for rotating geotree group choices. Placement/access results are returned by mutating caller-owned vectors and scalar pointers; nothing in the header is persisted to disk/config.

## Dependencies and Integration Points
Includes EOS logging, filesystem metadata types, layout id helpers, MGM namespace setup, and `mgm/fsview/FsView.hh`. The public argument structs depend on `eos::common::VirtualIdentity`. The scheduler is used by quota and MGM file command/open paths, while flat placement depends on `mgm/placement` implementations in the `.cc` file.

## Risks
- Raw pointers dominate the argument structs. `isValid()` catches many required fields, but optional fields and implementation assumptions such as `forcedspace` for flat access remain caller-sensitive.
- Strong types cover only placement file parameters; access arguments still use direct field mutation.
- `PlctPolicyFromString` returns `int` rather than `std::optional<tPlctPolicy>` or the enum type, requiring callers to handle `-1`.
- `getRequiredReplicas` truncates to `uint8_t`; the placement argument guard exists but can be bypassed if callers invoke the helper directly.

## Test Signals
Indirect coverage comes from file placement and flat scheduler tests under `unit_tests/mgm/placement`, plus integration call sites in quota and file open/create paths. The `PlacementArguments` builder and `AccessArguments::isValid()` are simple enough but do not appear to have dedicated unit coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/scheduler/Scheduler.hh -->
