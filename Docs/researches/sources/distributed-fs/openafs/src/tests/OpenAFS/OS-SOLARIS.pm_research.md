# sources/distributed-fs/openafs/src/tests/OpenAFS/OS-SOLARIS.pm

## Purpose
`OS-SOLARIS.pm` is an older OS-specific Perl configuration module that exports Solaris OpenAFS lifecycle command strings for tests.

## Important APIs, types, and functions
Package `OpenAFS::OS` exports `$openafsinitcmd`, mapping client/fileserver lifecycle actions to `modload`, `afsd`, `bosserver`, `bos shutdown`, and `pkill` command strings.

## Control flow
Loading the module initializes the hashref. Some actions are placeholders that echo unsupported stop/restart behavior.

## State and persistence behavior
Module state is the exported hashref. Executing commands can load kernel modules, start afsd/bosserver, or shut down/kill server processes.

## Dependencies and integration points
It depends on Solaris paths under `/usr/vice/etc` and `/usr/afs/bin`, plus older harness code using `$openafsinitcmd`.

## Risks
Hard-coded paths and `pkill` patterns are broad. Client stop/restart are explicitly unsupported. Package-name overlap with other OS modules can cause load-order confusion.

## Test signals
Verify module load/export and command behavior on a disposable Solaris OpenAFS test host.
