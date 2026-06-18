# sources/distributed-fs/openafs/src/tests/OpenAFS/OS.pm

## Purpose
`OS.pm` is the newer Perl OS abstraction for OpenAFS tests. It constructs platform-specific command providers and contains Unix/Linux implementations for starting/stopping servers, configuring clients, and force-stopping kernel client state.

## Important APIs, types, and functions
Package `OpenAFS::OS` exposes `create`, `new`, `_get_class`, and `command`. `OpenAFS::OS::Unix` provides `remove`, `fileserver_start`, `fileserver_stop`, `fileserver_restart`, `find_pids`, and `number_running`. `OpenAFS::OS::Linux` provides `get_commands`, `configure_client`, `client_forcestop`, and `list_modules`.

## Control flow
`create` chooses an implementation from configured `ostype`; currently only Linux is accepted. `new` stores paths, debug flag, sysconfig path, and command table. `command` retrieves a command or wraps a code reference with parameters. Linux `configure_client` writes an afs.rc configuration file from `OpenAFS::Dirpath` paths, creates cache and `/afs` directories, and `client_forcestop` tries unmount, afsd shutdown, kernel-module removal, and stale lock cleanup.

## State and persistence behavior
Objects store command tables and configuration paths. The module writes `test-afs-rc.conf`, creates/chmods cache directories and `/afs`, starts/stops bosserver, kills processes, removes kernel modules, and removes `/var/lock/subsys/afs`.

## Dependencies and integration points
It depends on `OpenAFS::Dirpath`, `OpenAFS::ConfigUtils::run`, init scripts, bos/bosserver/afsd paths, `/sbin/lsmod`, `/sbin/rmmod`, `ps`, and root privileges for client/server operations.

## Risks
Only Linux is supported despite separate older Solaris module. `fileserver_restart` calls `fileserver_stop()` and `fileserver_start()` without `$self->`, which is likely a bug under strict subs. Shell command strings are unquoted, and `find_pids` can match unintended command names. Force-stop operations are destructive on the host.

## Test signals
Test class selection, command lookup and parameter appending for strings and code refs, client config file content, cache/afs directory creation, module listing, force-stop idempotence, and fileserver stop behavior with zero/multiple bosserver processes.
