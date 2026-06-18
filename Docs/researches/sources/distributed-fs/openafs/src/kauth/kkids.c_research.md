# sources/distributed-fs/openafs/src/kauth/kkids.c

## Purpose
Manages the optional `kpwvalid` child process used by `kpasswd` to enforce local password-quality policy. It tries to find `kpwvalid` next to the running `kpasswd` binary and only uses it if the path is considered secure.

## Important APIs, Types, And Functions
Exports `init_child`, `password_bad`, `give_to_child`, and `terminate_child`. Internal helpers include `simplify_name`, `find_me`, `InAFS`, `ParseAcl`, `safestrtok`, `is_secure`, and `kpwvalid_is`. Static state includes `using_child`, `childin`, and `childout`.

## Control Flow
`init_child` resolves the executable path, checks that the parent directory is in AFS and that ACLs on each AFS path component grant write/admin power only to `system:administrators`, verifies a sibling `kpwvalid`, creates two pipes, forks, connects child stdin/stdout to the pipes, and execs `kpwvalid`. `give_to_child` sends the old password. `password_bad` sends a proposed password and reads an integer result. `terminate_child` kills the child on Unix; Windows disables the child process path.

## State And Persistence
State is a live child process and two stdio pipes. It reads filesystem metadata and AFS ACLs but does not persist data.

## Dependencies And Integration Points
It is used only by `kpasswd.c`. It depends on pioctl operations (`VIOC_FILE_CELL_NAME`, `VIOCGETAL`), AFS ACL rights constants, Unix process APIs, and `kpwvalid` protocol of writing an integer result to stdout.

## Risks And Test Signals
Risks include path-resolution races, symlink handling, fixed-size path buffers, incomplete ACL memory cleanup, pipe deadlocks if the child misbehaves, killing by pid without wait/close cleanup, and platform divergence on Windows. Test signals include secure and insecure directory detection, absence of `kpwvalid`, old-password handoff, rejection/acceptance protocol, child exec failure, and password-change fallback when no child is used.
