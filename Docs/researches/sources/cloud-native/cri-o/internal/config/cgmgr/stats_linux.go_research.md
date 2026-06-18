# sources/cloud-native/cri-o/internal/config/cgmgr/stats_linux.go

## Purpose
Process/cgroup stats conversion helpers.

## Important APIs, Types, and Functions
statsFromLibctrMgr obtains libcontainer stats and converts to internal stats. cgroupProcessStats aggregates pid count, file descriptor count, socket count, and ulimit count. addFdsForProcess reads /proc/<pid>/fd links and counts sockets; addUlimitsForProcess parses /proc/<pid>/limits.

## Control Flow
Stats path calls manager.GetStats, iterates pids, reads proc files, and builds CRI-O stats structures.

## State and Persistence
Reads /proc and cgroup stats; no persistence.

## Dependencies
Depends on opencontainers/cgroups stats and internal/lib/stats structures, os/readlink parsing.

## Integration Points
Feeds CRI-O metrics/status reporting for pod/container cgroups.

## Risks and Edge Cases
Processes can exit while reading; permission errors or proc races may undercount; parsing /proc/limits is format-sensitive.

## Test Signals
Runtime metrics tests and stats consumers validate behavior.
