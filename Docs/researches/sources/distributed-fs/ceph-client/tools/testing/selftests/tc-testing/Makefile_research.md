# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/Makefile

## Purpose
Registers tc-testing assets with kselftest.

## Important APIs, Types, And Functions
Adds `tdc.sh` to `TEST_PROGS` and installs files matching `action-ebpf`, `tdc*.py`, `Tdc*.py`, `plugins`, `plugin-lib`, `tc-tests`, and `scripts` through `TEST_FILES`, then includes `../lib.mk`.

## Control Flow
No custom build control beyond kselftest file staging. The actual runner is `tdc.sh`/Python code outside this assigned set.

## State And Persistence
No runtime state in this file.

## Dependencies And Integration Points
Depends on kselftest installation preserving Python plugins, JSON tests, helper scripts, and the eBPF action object. It pairs with `config` for kernel networking feature requirements.

## Risks
Missing a file pattern here can make installed tests fail even though they work in-tree. The Makefile assumes `action-ebpf` exists or is produced elsewhere.

## Test Signals
Installed kselftest directories contain the runner, Python modules, plugin libraries, JSON test cases, scripts, and eBPF helper object.
