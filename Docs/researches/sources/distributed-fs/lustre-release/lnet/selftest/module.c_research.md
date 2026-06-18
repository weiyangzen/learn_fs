# sources/distributed-fs/lustre-release/lnet/selftest/module.c

## Purpose
Provides LNet Selftest module entry and exit. It creates workqueues, starts SRPC/framework/console layers, checks wire layout, and unwinds partial initialization.

## Important APIs And Functions
Defines init-step constants, exported `lst_serial_wq` and `lst_test_wq`, `lnet_selftest_structure_assertion()`, `lnet_selftest_init()`, and `lnet_selftest_exit()`.

## Control Flow
`late_initcall_sync()` invokes initialization: assert SRPC wire struct sizes/offsets, run `libcfs_setup()`, allocate ordered serial workqueue, allocate per-CPT test workqueues, start SRPC, start framework, and initialize console. Exit uses a fallthrough switch to undo exactly the completed phases.

## State And Persistence
Runtime state is the init step and workqueue pointers. No persistent data exists. Cleanup assumes lower layers drain their work before workqueues are destroyed.

## Dependencies And Integration Points
Integrates libcfs setup, LNet CPT topology, SRPC startup/shutdown, framework startup/shutdown, console init/fini, and Linux module metadata.

## Risks
Wire ABI drift can corrupt cross-node messages, so the `BUILD_BUG_ON()` checks are critical. Error unwind depends on updating `lst_init_step` only after success. Partial per-CPT workqueue creation must be handled carefully.

## Test Signals
Build-time ABI assertion failures, load/unload tests, injected failures at each init phase, and clean workqueue destruction are key signals.
