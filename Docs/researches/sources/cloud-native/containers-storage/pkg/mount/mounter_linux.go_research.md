# sources/cloud-native/containers-storage/pkg/mount/mounter_linux.go

Purpose: implements Linux mount syscall sequencing for normal, bind, remount, read-only bind, and propagation changes.

Important APIs, types, and functions: constants `ptypes`, `pflags`, `broflags`, `none`; functions `isremount` and platform `mount`.

Control flow: `isremount` treats explicit `MS_REMOUNT`, empty device, or `none` device as remount-like. `mount` first applies non-propagation flags and data when appropriate, then applies propagation flags with a second mount call, then remounts bind mounts read-only when `MS_BIND|MS_RDONLY` are both present.

State and persistence: mutates the Linux mount namespace. No package-level state.

Dependencies and integration points: depends on `golang.org/x/sys/unix`; called by `mount.go` and `sharedsubtree_linux.go`.

Risks and edge cases: mount operations are privileged and namespace-sensitive. Multi-step bind read-only setup can leave intermediate state if a later step fails. Treating `device == "none"` as remount supports compatibility but affects call ordering.

Test signals: `mounter_linux_test.go` validates option outcomes in `/proc/self/mountinfo` across bind, propagation, read-only, and remount scenarios.
