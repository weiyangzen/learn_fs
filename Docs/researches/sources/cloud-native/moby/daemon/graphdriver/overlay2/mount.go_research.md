# sources/cloud-native/moby/daemon/graphdriver/overlay2/mount.go

Purpose: helper for overlay2 mounts whose option strings must be made relative to the driver home to fit the kernel page-size mount-data limit.

Important APIs and control flow: `mountFrom` starts a goroutine, locks it to an OS thread, unshares `CLONE_FS` so cwd changes do not leak to other threads, changes to the requested directory, and performs `unix.Mount`. The thread is deliberately not unlocked because its filesystem state cannot be restored safely.

State, dependencies, and risks: runtime state is a throwaway locked OS thread with isolated filesystem context. Dependencies are Linux `unshare`, `chdir`, and mount syscalls. It is called by `overlay2.Get` only when absolute mount data is too large and relative layer links are needed. Risks include thread leakage by design, syscall failure in restricted environments, and mount behavior depending on cwd isolation.
