# sources/distributed-fs/ceph-client/tools/testing/selftests/livepatch/test-syscall.sh

## Purpose

`test-syscall.sh` stresses livepatching of the `getpid` syscall while many processes are actively executing it. It checks that all selected tasks transition into the patched state.

## Important APIs, Types, and Functions

It starts multiple `test_klp-call_getpid` helpers, passes their PIDs through the `klp_pids` module parameter to `test_klp_syscall`, polls `/sys/kernel/test_klp_syscall/npids`, and uses harness livepatch load/unload functions.

## Control Flow and State

The script starts up to min(online CPUs, 128) busy helper processes, joins their PIDs into a comma-separated module parameter, loads the livepatch, waits until `npids` reaches zero, logs the remaining count, kills helpers, then disables and unloads the livepatch.

## Dependencies and Integration Points

It depends on syscall wrapper naming by architecture, livepatch transition mechanics, a custom sysfs counter exposed by the module, and process management.

## Risks and Test Signals

Risks are tasks never reaching a safe transition point, wrong syscall symbol names, sysfs counter races, or leaked helper processes. Signals are `npids` becoming 0, dmesg logging `Remaining not livepatched processes: 0`, and clean unpatching.
