<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/runconfig/hostconfig_test.go -->
# sources/cloud-native/moby/daemon/internal/runconfig/hostconfig_test.go

Purpose: tests non-Windows resource validation for host config.

Important APIs and types: `TestValidateResources`.

Control flow: table tests build `HostConfig.Resources` and `sysinfo.SysInfo` combinations, then call `validateResources`, expecting invalid-argument errors for unsupported CPU realtime settings, realtime runtime greater than period, and negative CPU shares when CPU shares are supported.

State and persistence: none.

Dependencies and integration: Linux/Unix build only; uses API container resources and sysinfo.

Risks: does not cover memory, blkio, cpuset, or Windows validators. Because CPU shares negative validation depends on support flag, unsupported systems may still pass invalid values to lower layers.

Test signals: focused coverage of CPU realtime and shares validation.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/runconfig/hostconfig_test.go -->
