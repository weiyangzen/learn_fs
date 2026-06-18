# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/main/sbin/kms.sh

## Purpose
`kms.sh` is a deprecated compatibility wrapper for controlling KMS.

## Important APIs, Types, and Functions
It supports `run`, `start`, `status`, and `stop`, prints usage, warns that users should call `hadoop [--daemon start|status|stop] kms`, locates `bin/hadoop` from `HADOOP_HOME` or relative to the script, and execs the Hadoop command with translated arguments.

## Control Flow
No arguments prints usage and exits. `run` maps to `hadoop kms`; daemon commands map to `hadoop --daemon <cmd> kms`; unknown commands print usage and exit 1. The final `exec` replaces the shell process.

## State and Persistence
It holds only transient shell variables and writes no persistent state.

## Dependencies and Integration Points
It depends on the Hadoop command-line launcher and the `hadoop-kms.sh` shell profile that implements the actual `kms` subcommand.

## Risks
As a deprecated wrapper, behavior can diverge from the main Hadoop launcher if argument semantics change. Relative path discovery assumes the standard Hadoop layout.

## Test Signals
Shell tests should verify command translation, deprecation warning, usage text, unknown-command exit status, `HADOOP_HOME` path selection, and relative path fallback.
