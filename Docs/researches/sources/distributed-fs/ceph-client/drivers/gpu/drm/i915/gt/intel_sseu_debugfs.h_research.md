# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_sseu_debugfs.h

## Purpose
`intel_sseu_debugfs.h` declares SSEU debugfs status and registration functions.

## Important APIs, Types, And Functions
It forward-declares `struct intel_gt`, `struct dentry`, and `struct seq_file`, and declares `intel_sseu_status()` plus `intel_sseu_debugfs_register()`.

## Control Flow
There is no runtime logic in the header. GT debugfs setup includes it to register files, while top-level debugfs status code can call the status printer.

## State, Persistence, And Dependencies
The header stores no state and has minimal dependencies through forward declarations.

## Integration Points
It links GT debugfs code with the implementation in `intel_sseu_debugfs.c`.

## Risks
Callers must provide a valid live `intel_gt` and `seq_file`; runtime PM and platform support checks happen in the implementation.

## Test Signals
Compile coverage with debugfs enabled and smoke reads of `sseu_status`/`sseu_topology` validate the header contract.
