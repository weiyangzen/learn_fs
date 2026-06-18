# sources/cloud-native/moby/daemon/volume/local/local_unix.go

## Purpose
Unix implementation of local driver option validation, mount/unmount behavior, quota application, mount restoration, and creation time.

## Important APIs, Types, And Functions
Defines `optsConfig` with mount type/options/device and quota. Implements `Root.validateOpts`, `localVolume.setOpts`, `needsMount`, `getMountOptions`, `mount`, `postMount`, `unmount`, `restoreIfMounted`, and `CreatedAt`.

## Control Flow
Validation rejects unknown options, invalid size values, size without quota support, CIFS device URLs with embedded ports, and missing mandatory companion options. `setOpts` stores mount and quota settings to `opts.json`. `getMountOptions` rewrites NFS/CIFS `addr=` hostnames and CIFS device hostnames to resolved IPs. `mount` calls `mount.Mount`, redacting CIFS passwords from errors. `postMount` applies quota. `unmount` tolerates already-unmounted paths if mountinfo confirms absence. Startup `restoreIfMounted` marks an option-backed `_data` path as mounted without increasing count.

## State And Persistence
Persists option configuration via common `saveOpts`. Mount and quota state live in the host kernel/filesystem, while active flags are in-memory.

## Dependencies And Integration Points
Depends on go-units, daemon quota, Moby mount and mountinfo packages, net/url/IP resolution, errdefs, and syscall stat ctime.

## Risks
DNS rewriting can surprise users and must preserve escaped CIFS paths. Password redaction only covers `password=<value>` in mount options. Mount restoration without refcount relies on live restore later incrementing usage. Quota support varies by filesystem.

## Test Signals
Linux tests cover quota, mandatory options, CIFS URL restrictions, tmpfs mounting, mountinfo checks, and host resolution behavior.
