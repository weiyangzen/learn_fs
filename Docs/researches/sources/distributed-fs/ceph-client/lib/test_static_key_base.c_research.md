# sources/distributed-fs/ceph-client/lib/test_static_key_base.c

## Purpose

`sources/distributed-fs/ceph-client/lib/test_static_key_base.c` is a support module for static key testing. It exports old-style and new-style static keys in known initial and inverted states so another module can verify external static branch behavior. The source was read as a complete 61-line file.

## Important APIs, Types, and Functions

The file defines and exports `base_old_true_key`, `base_inv_old_true_key`, `base_old_false_key`, `base_inv_old_false_key`, `base_true_key`, `base_inv_true_key`, `base_false_key`, and `base_inv_false_key`. It uses `STATIC_KEY_INIT_TRUE`, `STATIC_KEY_INIT_FALSE`, `DEFINE_STATIC_KEY_TRUE`, `DEFINE_STATIC_KEY_FALSE`, `EXPORT_SYMBOL_GPL`, `static_key_enabled`, `static_key_disable`, and `static_key_enable`. Functions are `invert_key`, `test_static_key_base_init`, and `test_static_key_base_exit`.

## Control Flow

On load, `test_static_key_base_init` flips the four `base_inv_*` keys from their declared state. The normal `base_*` keys remain in their initial state. Exit does nothing.

## State and Persistence Behavior

The static keys are global exported module state while the module is loaded. They are modified once at initialization and then serve as external test fixtures. No file persistence exists.

## Dependencies and Integration Points

Direct includes are `<linux/module.h>` and `<linux/jump_label.h>`. Integration is with the jump-label/static-key subsystem and with `test_static_keys.c`, which declares these symbols as `extern`.

## Risks and Edge Cases

This module must be loaded before the consumer test module resolves the exported symbols. Static key enable/disable operations patch branch sites and must be used in contexts allowed by the jump-label subsystem. The support module does not restore inverted keys on exit, relying on module unload cleanup.

## Test Signals

The module itself returns `0` if loaded. Its real signal is that `test_static_keys.c` can link against the exported symbols and observe expected initial/inverted states.
