# sources/cloud-native/moby/daemon/libnetwork/internal/resolvconf/resolvconf_path.go

## Purpose
Chooses which host resolv.conf file libnetwork should read. It detects the common systemd-resolved stub resolver case and redirects legacy networking to systemd's generated resolver file.

## Important APIs, Types, And Functions
- `defaultPath` is `/etc/resolv.conf`.
- `alternatePath` is `/run/systemd/resolve/resolv.conf`.
- `Path()` returns the selected path, using `sync.Once` to perform detection only once per process.

## Control Flow
On first call, `Path` loads `/etc/resolv.conf`. If loading fails, it silently keeps the default path because the same error will surface to later open/read callers. If exactly one nameserver exists and it is `127.0.0.53`, it records the alternate systemd-resolved path and logs the detection.

## State And Persistence
The selected path is process-global in `pathAfterSystemdDetection`. There is no filesystem mutation. Because detection runs once, changes to host resolver configuration after first call are not observed.

## Dependencies And Integration Points
Depends on `Load` from the same package and `netip` for comparing the stub resolver address. It is used by Docker DNS setup code before parsing host resolver state.

## Risks
The heuristic only handles the exact single-nameserver systemd stub case. Multi-nameserver files including `127.0.0.53` stay on `/etc/resolv.conf`. The one-time cache is efficient but stale if systemd-resolved state changes while the daemon runs.

## Test Signals
No direct test file in this subset targets `Path`; behavior is indirectly protected by `resolvconf.go` parser tests. Comments document that the alternate path is mainly for legacy networking and may become unnecessary after legacy networking removal.
