<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/pkg/util/kernel/version.go -->
## sources/control-plane/ceph-csi/pkg/util/kernel/version.go

Purpose: obtains and evaluates Linux kernel versions against feature support requirements, including enterprise backports.

APIs and types: `GetKernelVersion` wraps `unix.Uname` and trims NUL bytes from release. `KernelVersion` describes minimum or backport-supported version fields. `parseKernelRelease` extracts version, patchlevel, sublevel, and numeric extra version from release strings. `CheckKernelSupport` compares a release against supported version rules, with generic minimum checks or strict distro/backport checks.

State and persistence: reads current kernel release via syscall; no persistence.

Dependencies: `golang.org/x/sys/unix`, internal log, string parsing.

Integration points: used by Ceph-CSI feature gates such as quota and deep-flatten support decisions.

Risks: parser accepts some suffix forms like `5.12xlinux` as version 5.12, which tests document. Backport matching uses substring containment for distribution. Warnings/errors are logged instead of returned with details because public API returns bool.

Test signals: `version_test.go` covers syscall result shape, parser good/bad releases, quota support, and deep-flatten support including RHEL-style backports.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/pkg/util/kernel/version.go -->
