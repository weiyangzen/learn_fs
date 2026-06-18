# sources/cloud-native/containers-storage/types/options_linux.go

Purpose: Linux storage defaults and rootless overlay capability heuristic.

Important APIs and control flow: defines rootful defaults `/run/containers/storage`, `/var/lib/containers/storage`, system config `/usr/share/containers/storage.conf`, and override `/etc/containers/storage.conf`. `canUseRootlessOverlay` first checks for `fuse-overlayfs`; if absent, it reads kernel release through `unix.Uname` and returns true for kernels >= 5.13 or any 6.x+ kernel.

State and persistence: no persistence. The function reads current executable lookup state and kernel version.

Dependencies and integration: used by rootless driver selection in `getRootlessStorageOpts`. Depends on `exec.LookPath`, `golang.org/x/sys/unix`, and simple version parsing.

Risks: kernel-version heuristics can be wrong for backports or vendor kernels; comments note this is only a heuristic and packaging may install explicit config. `strings.Split(string(uts.Release[:]), ".")` includes trailing NUL data but `Atoi` on the first numeric components usually works.

Test signals: `options_test.go` accepts either `overlay` or `vfs` when capability depends on host environment; direct deterministic tests would need fakes.
