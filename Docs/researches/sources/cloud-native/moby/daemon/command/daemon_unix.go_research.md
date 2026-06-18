<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/command/daemon_unix.go -->
# sources/cloud-native/moby/daemon/command/daemon_unix.go

## Purpose
Provides Unix-specific daemon command behavior: default config paths, umask normalization, SIGHUP reload, swarm run root, API port reservation, cgroup parent naming, and containerd startup selection.

## Important APIs, Types, And Functions
`getDefaultDaemonConfigDir`, `getDefaultDaemonConfigFile`, `setDefaultUmask`, `daemonCLI.setupConfigReloadTrap`, `getSwarmRunRoot`, `allocateDaemonPort`, `newCgroupParent`, and `daemonCLI.initContainerd`.

## Control Flow
RootlessKit toggles XDG config lookup through package state. SIGHUP is delivered to a goroutine that repeatedly invokes `reloadConfig`. TCP listener addresses are parsed, hostnames resolved, and each host IP is reserved in libnetwork's port allocator.

## State And Persistence Behavior
The file mutates process umask and installs a process signal handler. Port reservations live in the singleton port allocator. No disk writes occur directly.

## Dependencies And Integration Points
Integrates with `daemon.UsingSystemd`, `daemon/config`, `portallocator`, `homedir`, `os/signal`, and `golang.org/x/sys/unix`.

## Risks And Test Signals
Risks include wrong XDG path selection, surprising process-wide umask effects, hostname resolution failures preventing bind, and systemd cgroup parent formatting. Unix command tests cover config merge behavior; listener tests outside this item exercise listener inheritance.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/command/daemon_unix.go -->
