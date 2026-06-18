# sources/distributed-fs/openafs/src/tests/OpenAFS/OS-LINUX.pm

## Purpose
`OS-LINUX.pm` is an older OS-specific Perl configuration module that exports Linux init command strings for OpenAFS tests.

## Important APIs, types, and functions
Package `OpenAFS::OS` exports `$openafsinitcmd`, a hashref mapping client and fileserver lifecycle names to `/etc/init.d` commands.

## Control flow
Loading the module initializes the hash and returns true. There are no functions.

## State and persistence behavior
The only module state is the exported hashref. The command strings, when used, start/stop/restart OpenAFS client and fileserver services.

## Dependencies and integration points
It depends on SysV-style `/etc/init.d/openafs-client` and `/etc/init.d/openafs-fileserver` scripts and older harness code expecting `$openafsinitcmd`.

## Risks
Hard-coded init paths do not work on systemd-only or custom-install systems. The package name overlaps `OS.pm`, so load order matters.

## Test signals
Verify module load/export, expected keys, and command availability on target Linux test hosts.
