<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/info_windows.go -->
# sources/cloud-native/moby/daemon/info_windows.go

Purpose: provides Windows stubs for platform-specific info helpers that are Unix-specific elsewhere.

Important APIs and control flow: `fillPlatformInfo` and `fillPlatformVersion` return nil without adding fields. `fillDriverWarnings` is empty. `cgroupNamespacesEnabled`, `Rootless`, and `noNewPrivileges` all return false.

State and persistence: no state is read or written.

Dependencies and integration: selected on Windows to satisfy shared system info code without Unix cgroup/rootless/runtime behavior.

Risks: Windows system info lacks the Unix fields populated in `info_unix.go`, so callers must treat platform-specific fields as optional.

Test signals: compile-time coverage on Windows; no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/info_windows.go -->
