<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/rpm/service-files/lizardfs-chunkserver.service -->
# sources/distributed-fs/lizardfs/rpm/service-files/lizardfs-chunkserver.service

## Purpose
Systemd wrapper for the LizardFS chunkserver daemon.

## Important APIs, Types, and Functions
Defines `Type=forking` with `/usr/sbin/mfschunkserver start`, `stop`, and `reload` commands. It is ordered after `network.target` and restarts on abort.

## Control Flow, State, and Persistence
Systemd delegates daemonization and PID handling to the legacy `mfschunkserver` control command. Persistent chunkserver state is outside the unit, in the daemon configuration, chunk storage paths, and runtime PID/state files maintained by the service binary.

## Dependencies and Integration Points
Integrates with packaged `/usr/sbin/mfschunkserver`, LizardFS chunkserver configuration, local disk mounts, and the master registration path.

## Risks and Test Signals
Risks include `Type=forking` correctness depending on the script/binary's daemonization behavior, no explicit dependency on mounted chunk disks, minimal systemd sandboxing, and restart-on-abort not covering clean unexpected exits. Test signals are start/stop/reload through systemd, chunkserver registration with the master, behavior when storage directories are missing, and systemd recognizing the forked process as active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/rpm/service-files/lizardfs-chunkserver.service -->
