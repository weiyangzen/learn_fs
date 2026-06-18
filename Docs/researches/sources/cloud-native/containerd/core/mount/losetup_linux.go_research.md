# sources/cloud-native/containerd/core/mount/losetup_linux.go

Purpose: provides Linux loop device setup, attach, detach, autoclear, and direct-IO configuration helpers.

Important APIs and types: constants `loopControlPath`, `loopDevFormat`, `ebusyString`; `LoopParams`; `getFreeLoopDev`; `setupLoopDev`; `SetupLoop`; `setLoopAutoclear`; `removeLoop`; `AttachLoopDevice`; and `DetachLoopDevice`.

Control flow: `getFreeLoopDev` opens `/dev/loop-control` and uses `LOOP_CTL_GET_FREE`. `setupLoopDev` opens backing file and loop device read-only or read-write, uses `LOOP_CONFIGURE` on kernels >= 5.8 to atomically configure fd, filename, readonly, autoclear, and direct IO flags, otherwise falls back to `LOOP_SET_FD`, `LOOP_SET_STATUS64`, and optional `LOOP_SET_DIRECT_IO`, cleaning up on errors. `SetupLoop` retries up to 99 times when free-loop races surface as EBUSY, with randomized backoff. `setLoopAutoclear` toggles `LO_FLAGS_AUTOCLEAR`. `AttachLoopDevice` attaches and returns the loop path after closing the handle. `DetachLoopDevice` clears each supplied loop fd.

State and persistence: manipulates kernel loop device state and backing file association. Autoclear determines whether kernel cleanup happens on last close.

Dependencies and integration: depends on Linux loop ioctls from `x/sys/unix`, kernel version helper, randutil, and filesystem device nodes. Used by loopback mount handler and tests.

Risks: string matching `device or resource busy` is used for retry classification. Kernel version probing controls use of modern atomic loop configuration. Direct IO and readonly flags depend on kernel support. Attach without autoclear leaves cleanup responsibility to caller.

Test signals: `losetup_linux_test.go` covers missing backing file, readonly write failure, read-write write success, attach/detach, autoclear true cleanup, and autoclear false manual cleanup.
