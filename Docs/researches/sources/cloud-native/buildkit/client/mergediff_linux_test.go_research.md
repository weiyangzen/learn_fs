# sources/cloud-native/buildkit/client/mergediff_linux_test.go

Purpose: Linux-only filesystem test helpers for merge/diff tests that need FIFOs and character devices.

Important APIs/types/functions: build tag `linux`; `mknod` returns an `fstest.Applier` invoking `unix.Mknod`; `mkfifo` and `mkchardev` specialize it with `S_IFIFO` and `S_IFCHR`.

Control flow: helper joins the requested path under the fstest root and applies the node creation with requested mode/device major/minor.

State and persistence: creates filesystem nodes in temporary test roots when applied.

Dependencies/integration points: containerd continuity `fstest`, `golang.org/x/sys/unix`, and merge/diff tests outside this listed subset.

Risks/test signals: requires Linux privileges/capabilities appropriate for device node creation; failures surface in tests using these appliers. Non-Linux fallback is in `mergediff_nolinux_test.go`.
