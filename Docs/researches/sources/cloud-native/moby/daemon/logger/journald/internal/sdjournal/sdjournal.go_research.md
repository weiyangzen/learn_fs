# sources/cloud-native/moby/daemon/logger/journald/internal/sdjournal/sdjournal.go

Purpose: cgo wrapper around libsystemd `sd_journal` for reading journal entries.

Important APIs/types/functions: `Journal` wraps `*C.sd_journal` and is marked no-copy. Constructors `Open` and `OpenDir`; navigation `Next`, `Previous`, `PreviousSkip`, `SeekHead`, `SeekTail`, `SeekRealtime`; eventing `InitializeInotify`, `Wait`, `Process`; data `Realtime`, `Data`, `SetDataThreshold`; status constants `StatusNOP`, `StatusAPPEND`, `StatusINVALIDATE`.

Control flow/state/persistence: constructors allocate C journal handles and attach finalizers. Methods translate negative C return codes to `syscall.Errno` errors. `Data` enumerates all fields into a Go map after `restartData`, favoring one O(N) pass over repeated linear lookups.

Dependencies/integration: `#cgo pkg-config: libsystemd`, `systemd/sd-journal.h`, runtime finalizers, `runtime.LockOSThread` contract enforced by callers in `journald/read.go`.

Risks: thread-affinity is critical; a `Journal` must remain on one OS thread. Seek APIs have documented conceptual-position edge cases, handled in higher-level reader code. cgo/build constraints limit availability.

Test signals: journald read tests exercise this wrapper through fake journal files when built with Linux, cgo, and journald tags.
