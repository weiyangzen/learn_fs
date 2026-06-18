<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/cgroup/Makefile -->
# sources/distributed-fs/ceph-client/samples/cgroup/Makefile

## Purpose
The cgroup samples `Makefile` declares two userspace sample programs for cgroup event listening.

## Important APIs, Types, And Functions
It adds `cgroup_event_listener` and `memcg_event_listener` to `userprogs-always-y` and appends `-I usr/include` to `userccflags`.

## Control Flow
Kbuild consumes these variables to compile the listed userspace binaries whenever samples are built.

## State And Persistence
There is no runtime state. The persistent effect is build inclusion of the two sample tools.

## Dependencies And Integration Points
It integrates with the kernel samples Kbuild infrastructure and the userspace include staging path.

## Risks And Edge Cases
Missing the include flag can break builds against generated UAPI headers. Adding binaries here makes them always built with the cgroup samples.

## Test Signals
`make samples/cgroup/` should build both listener binaries without missing-header errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/cgroup/Makefile -->
