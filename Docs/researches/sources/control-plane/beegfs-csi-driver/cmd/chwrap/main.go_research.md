<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/cmd/chwrap/main.go -->
# sources/control-plane/beegfs-csi-driver/cmd/chwrap/main.go

## Purpose
`chwrap` is a small helper executable used through symlinks inside the CSI driver container to execute host-installed commands from a `/host` chroot.

## Important APIs, Types, and Functions
`validBinary()` uses `unix.Lstat()` to accept readable/executable regular files or symlinks. `findBinary()` searches host paths for the invoked binary, prioritizing plugin-owned BeeGFS client utilities under `/var/lib/kubelet/plugins/beegfs.csi.netapp.com/client/`, then `/usr/local`, `/usr`, and root-level `sbin`/`bin`. `modifyEnv()` replaces `PATH` with a host-appropriate path. `main()` derives the command name from `argv[0]`, locates it under `/host`, chroots to `/host`, changes directory to `/`, and `exec`s the host command.

## Control Flow
The program is normally invoked as a symlink named `mount`, `umount`, `beegfs`, or similar. It strips path prefixes from `argv[0]`, searches `/host`, exits 127 if not found, performs `chroot("/host")`, `chdir("/")`, and then replaces itself with the intended host command using the original argv.

## State and Persistence
It persists no state. It changes process root and environment before exec. The host command may persist state depending on the command invoked.

## Dependencies and Integration Points
It depends on `golang.org/x/sys/unix`, the container having `/host` mounted to the node filesystem, and the Dockerfile placing symlinked commands earlier in `PATH`. CSI controller and node manifests mount `/host` and use privileged containers to make this possible.

## Risks
The wrapper intentionally executes host binaries from a privileged container, so path search order is security-sensitive. `validBinary()` accepts symlinks if readable/executable bits allow, which is needed for absolute host symlinks but expands trust to host filesystem links. `panic()` on chroot/chdir/exec failure can expose stack traces.

## Test Signals
Tests should cover binary search order, symlink handling via `Lstat`, PATH replacement, command-not-found exit code 127, and integration in a container with `/host` mounted.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/cmd/chwrap/main.go -->
