# sources/cloud-native/moby/contrib/check-config.sh

## Purpose
Checks a Linux kernel configuration for Docker-relevant features and reports required, optional, and limit-related support.

## APIs, Types, And Functions
Important shell helpers include `is_set`, `is_set_in_kernel`, `is_set_as_module`, color/wrap helpers, `check_flag`, `check_flags`, `check_command`, `check_device`, `check_sysctl`, and `check_limit_over`.

## Control Flow, State, And Integration
The script chooses a kernel config path, provides `zgrep` fallback behavior, detects terminal color support, derives kernel version pieces, then checks kernel config symbols, commands, devices, sysctls, and cgroup/storage/networking capabilities. It reports to stdout and accumulates an exit code.

## Risks And Test Signals
Risks include stale kernel option lists, distro-specific config paths, false negatives for module support, and shell portability. Integration is with administrator diagnostics for Docker host readiness.
