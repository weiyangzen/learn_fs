# sources/cloud-native/moby/contrib/init/sysvinit-debian/docker

## Purpose
Provides a Debian-style SysV init script for starting, stopping, restarting, and checking dockerd.

## APIs, Types, And Functions
The script defines LSB metadata, configurable variables such as `DOCKERD`, pid files, logfile, and `DOCKER_OPTS`, plus `fail_unless_root` and case handlers for `start`, `stop`, `restart`, `force-reload`, and `status`.

## Control Flow, State, And Integration
On start, it validates root and executable presence, prepares the log file, raises limits, and invokes `start-stop-daemon` with dockerd pidfile arguments. Stop and status use pid files and LSB helper functions. Persistent state includes pid files and `/var/log/docker.log`.

## Risks And Test Signals
Risks include stale pid files, permission issues, shell differences for ulimit behavior, and outdated init assumptions. Integration is with Debian LSB init and `/etc/default/docker`.
