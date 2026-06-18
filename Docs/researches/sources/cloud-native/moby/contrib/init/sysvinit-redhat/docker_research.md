# sources/cloud-native/moby/contrib/init/sysvinit-redhat/docker

## Purpose
Provides a Red Hat-style SysV init script for dockerd.

## APIs, Types, And Functions
The script defines chkconfig metadata, paths for `unshare`, `dockerd`, pidfile, lockfile, logfile, and optional `/etc/sysconfig/docker` settings. Functions include `prestart`, `start`, `stop`, `restart`, `reload`, `force_reload`, status helpers, and `check_for_cleanup`.

## Control Flow, State, And Integration
Start verifies executability, cleans stale pid files, starts cgconfig if needed, launches dockerd in a new mount namespace via `unshare -m`, waits for the pidfile, and writes lock/log state. Stop uses `killproc` and removes the lock on success.

## Risks And Test Signals
Risks include stale pid handling, cgconfig dependency failures, mount namespace assumptions, fixed paths, and log growth. Integration is with Red Hat service management and `/etc/sysconfig/docker`.
