# sources/distributed-fs/ceph-client/tools/testing/selftests/livepatch/test-livepatch.sh

## Purpose

`test-livepatch.sh` is the broad functional livepatch script. It validates vmlinux function patching, multiple livepatch stacking, atomic replacement, patching functions in a separately loaded module, and loading a module-targeting livepatch before its target module appears.

## Important APIs, Types, and Functions

It uses harness module helpers, `/proc/cmdline`, `/proc/meminfo`, `/proc/test_klp_mod_target`, livepatch sysfs module counts, and modules `test_klp_livepatch`, `test_klp_syscall`, `test_klp_callbacks_demo`, `test_klp_atomic_replace`, `test_klp_mod_target`, and `test_klp_mod_patch`.

## Control Flow and State

Each scenario loads livepatch modules, reads proc files to prove redirection, disables patches through sysfs, unloads modules, and compares dmesg. Atomic replacement verifies old patches disappear from livepatch sysfs while the replacement remains active. Module patching scenarios check both target-before-patch and patch-before-target ordering.

## Dependencies and Integration Points

It depends on livepatch stacking and replace semantics, procfs show functions, module notifier patching, and exact dmesg checking.

## Risks and Test Signals

Risks include stale patches remaining after disable, wrong stack behavior, atomic replace not disabling old patches, and module patching not applying at module load. Signals are proc file contents switching between original and patched strings and exact transition logs.
