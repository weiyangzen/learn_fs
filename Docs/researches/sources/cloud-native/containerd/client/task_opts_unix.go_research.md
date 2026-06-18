# Research: sources/cloud-native/containerd/client/task_opts_unix.go

## Purpose
Provides Unix-specific task creation options for runc behavior, shim cgroups, and IO ownership.

## Important APIs, Control Flow, And State
`WithNoNewKeyring` and `WithNoPivotRoot` fetch or initialize runc options through `TaskInfo.getRuncOptions` and set `NoNewKeyring` or `NoPivotRoot`. `WithShimCgroup` records the shim cgroup path. `WithUIDOwner` and `WithGIDOwner` set `IoUid` and `IoGid` used by the shim when creating IO FIFOs/pipes. The file mutates task creation option state only; runtime effects occur later in shim/runc create.

## Dependencies And Integration
Depends on `context` and shared task/runc option structures. It integrates with Linux shim create options and manager cgroup placement.

## Risks And Test Signals
Risks include errors if task runtime options are not runc options, invalid cgroup paths, and IO ownership mismatches. Tests should cover option mutation, existing runtime options preservation, and invalid runtime option formats.
