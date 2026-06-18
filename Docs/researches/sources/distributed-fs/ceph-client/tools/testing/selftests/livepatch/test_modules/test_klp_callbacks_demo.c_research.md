# sources/distributed-fs/ceph-client/tools/testing/selftests/livepatch/test_modules/test_klp_callbacks_demo.c

## Purpose

`test_klp_callbacks_demo.c` is the main callback livepatch module. It patches no-op objects for vmlinux and `test_klp_callbacks_mod`, patches `busymod_work_func` in `test_klp_callbacks_busy`, and logs every callback.

## Important APIs, Types, and Functions

It defines parameter `pre_patch_ret`, callback helpers `pre_patch_callback()`, `post_patch_callback()`, `pre_unpatch_callback()`, `post_unpatch_callback()`, replacement `patched_work_func()`, and `klp_object` entries with callbacks.

## Control Flow and State

On load it enables a patch. Each callback logs object identity and module state; `pre_patch_callback()` can fail with the configured return code. For the busy module, the function replacement participates in transition-stall tests.

## Dependencies and Integration Points

It depends on livepatch callbacks, target modules named in `klp_object.name`, and scripts that compare exact logs across notifier paths.

## Risks and Test Signals

Risks include wrong callback ordering, missing callbacks for module coming/going, and incorrect failure propagation. Signals are exact logs with `MODULE_STATE_*` text and expected `insmod` failure when `pre_patch_ret` is negative.
