# sources/distributed-fs/ceph-client/tools/testing/selftests/livepatch/test_modules/test_klp_mod_patch.c

## Purpose

`test_klp_mod_patch.c` livepatches a function supplied by the separate `test_klp_mod_target` module.

## Important APIs, Types, and Functions

It defines replacement `livepatch_mod_target_show()`, maps old function name `test_klp_mod_target_show`, targets `klp_object.name = "test_klp_mod_target"`, and enables the patch in module init.

## Control Flow and State

The livepatch can be loaded before or after the target module. When both are present, reads from `/proc/test_klp_mod_target` call the replacement and show the livepatch module name.

## Dependencies and Integration Points

It depends on livepatch module-object matching and the target module's non-inlined show function.

## Risks and Test Signals

Risks include target function inlining/renaming and module notifier failures. Signals are the proc entry switching from original output to patched output and back.
