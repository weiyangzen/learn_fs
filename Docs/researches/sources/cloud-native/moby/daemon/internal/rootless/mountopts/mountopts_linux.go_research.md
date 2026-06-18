<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/rootless/mountopts/mountopts_linux.go -->
# sources/cloud-native/moby/daemon/internal/rootless/mountopts/mountopts_linux.go

Purpose: computes mount flags locked by `CL_UNPRIVILEGED` for a path so rootless bind mounts can preserve required options.

Important APIs and types: `UnprivilegedMountFlags(path string) ([]string, error)`.

Control flow: calls `unix.Statfs`, checks selected mount flag bits, and returns option strings for readonly, nodev, noexec, nosuid, noatime, relatime, and nodiratime.

State and persistence: reads filesystem mount state; no mutation.

Dependencies and integration: used by rootless mount setup to avoid kernel rejections when remounting with options.

Risks: returned flag order depends on map iteration, so callers should not rely on ordering. It only includes a known subset of locked flags.

Test signals: no direct tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/rootless/mountopts/mountopts_linux.go -->
