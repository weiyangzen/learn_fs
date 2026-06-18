# sources/cloud-native/moby/integration/system/cgroupdriver_systemd_test.go

## Purpose
Regression test for setting container memory limits when a daemon runs with the native systemd cgroup driver.

## Important APIs, Types, And Functions
- `hasSystemd` checks `/run/systemd/system` to decide whether systemd is the host init system.
- `TestCgroupDriverSystemdMemoryLimit` starts a daemon with `--exec-opt native.cgroupdriver=systemd`, disables iptables, creates a container with 64 MiB memory limit, starts it, and inspects host config.

## Control Flow
The test skips Windows and non-systemd hosts, runs in parallel, starts an isolated daemon with busybox loaded, creates and starts a container, then inspects it.

## State And Persistence
Temporary daemon root, cgroup configuration, and container state are created. Container removal and daemon stop are deferred.

## Dependencies And Integration Points
Requires Linux with systemd, cgroup support, a runnable local daemon, test daemon helpers, and container integration helpers. It integrates daemon cgroup-driver configuration with container resource setup.

## Risks And Edge Cases
Host systemd detection is filesystem-based and may be false in containers. The test cannot run on Windows and may fail on hosts without suitable cgroup/systemd support.

## Test Signals
Passing confirms `ContainerInspect.HostConfig.Memory` equals `64 * 1024 * 1024` under the systemd cgroup driver.
