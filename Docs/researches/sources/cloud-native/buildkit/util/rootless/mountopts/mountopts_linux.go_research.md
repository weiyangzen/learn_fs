<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/rootless/mountopts/mountopts_linux.go -->
# sources/cloud-native/buildkit/util/rootless/mountopts/mountopts_linux.go

Purpose: preserves kernel-locked unprivileged mount flags on bind mounts in rootless/user-namespace scenarios.

Important APIs and types: `UnprivilegedMountFlags`, `FixUp`, and `FixUpOCI`.

Control flow: `UnprivilegedMountFlags` calls `unix.Statfs` and maps locked filesystem flags to mount option strings such as `ro`, `nodev`, `noexec`, and `nosuid`. `FixUp` and `FixUpOCI` scan mount option lists for `bind`/`rbind`, fetch unprivileged flags for the mount source, append and dedupe them, and write the updated mount back.

State and persistence: no persistent state; reads kernel mount flags for the supplied path.

Dependencies and integration: uses containerd mount types, OCI runtime spec mounts, BuildKit slice dedupe helper, and `x/sys/unix`. Integrated where BuildKit prepares mounts for rootless execution.

Risks: `Statfs` errors fail the entire fixup. Only bind/rbind mounts are modified. Option order after dedupe depends on append/dedupe behavior.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/rootless/mountopts/mountopts_linux.go -->
