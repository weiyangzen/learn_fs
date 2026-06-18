# sources/distributed-fs/ceph-client/drivers/spmi/spmi-devres.c

## Purpose

`spmi-devres.c` provides device-managed wrappers for SPMI controller allocation and registration. It lets platform drivers tie `spmi_controller_put()` and `spmi_controller_remove()` to parent-device devres cleanup instead of open-coding unwind paths.

## Important APIs, Types, And Functions

The exported APIs are `devm_spmi_controller_alloc()` and `devm_spmi_controller_add()`. Release callbacks are `devm_spmi_controller_release()` for controller references and `devm_spmi_controller_remove()` for registered controllers.

## Control Flow And State

`devm_spmi_controller_alloc()` allocates a devres slot containing a controller pointer, calls `spmi_controller_alloc(parent, size)`, stores the returned pointer, and adds the release action to the parent. If allocation fails, it frees the devres slot and returns the framework error pointer.

`devm_spmi_controller_add()` allocates a second devres slot, calls `spmi_controller_add(ctrl)`, and records a remove action only after successful registration. On add failure, it frees the devres slot and returns the error. During parent-device teardown, devres unwinds in reverse order, removing the registered controller and then dropping the allocation reference.

## State And Persistence Behavior

The managed state is the controller pointer stored in parent devres records. No hardware state is touched here. Lifetime ordering depends on normal devres LIFO cleanup.

## Dependencies And Integration Points

This file depends on the SPMI core allocation, add, remove, and put APIs plus generic devres. Platform drivers such as the Hisilicon, Apple, and MediaTek SPMI controllers use these helpers to reduce manual error paths.

## Risks And Test Signals

Risks include callers mixing managed and unmanaged removal for the same controller, or assuming `devm_spmi_controller_add()` owns the allocation when it only registers a removal action. Test signals are probe-failure unwinds before and after controller add, driver unbind, module unload, repeated bind/unbind under KASAN/KMEMLEAK, and checking that controller children disappear before the allocation reference is released.
