<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/qcomtee/primordial_obj.c -->
# sources/distributed-fs/ceph-client/drivers/tee/qcomtee/primordial_obj.c

## Purpose

`primordial_obj.c` defines the kernel-hosted primordial QTEE callback object. It provides privileged native services to secure world: mapping a Linux memory object, yielding the current thread, and sleeping for a requested duration.

## Important APIs, Types, and Functions

The supported operation IDs are `QCOMTEE_OBJECT_OP_MAP_REGION`, `QCOMTEE_OBJECT_OP_YIELD`, and `QCOMTEE_OBJECT_OP_SLEEP`. `struct qcomtee_mapping_info` is the packed ABI returned to QTEE with physical address, length, and permissions. `qcomtee_primordial_obj_dispatch()` implements the operations. `qcomtee_primordial_obj_notify()` releases a produced map object if the callback response fails. The exported static object is `qcomtee_primordial_object`.

## Control Flow

For YIELD, dispatch calls `cond_resched()` and sets no output object. For SLEEP, it requires one input buffer of at least `u32`, reads milliseconds from the shared callback buffer, calls `msleep()`, and sets no output object. For MAP_REGION, it requires three arguments: output buffer for mapping info, input object for the memory object, and output object for the mapping object. It invokes `qcomtee_mem_object_map()`, places the mapping object into `args[2]`, stores it in `oic->data` for later notify cleanup, and puts the input memory-object reference.

## State and Persistence Behavior

The primordial object is static and not refcounted like normal callback objects. Per-call state is only `oic->data`, used to remember an output mapping object until the response is accepted by QTEE. No data persists after callback completion except references QTEE retains to the returned mapping object.

## Dependencies and Integration Points

This file integrates with `core.c` through the reserved non-secure primordial object ID and callback dispatch path. It depends on `mem_obj.c` for mapping, on the qcomtee object argument ABI, and on kernel scheduler/timer helpers `cond_resched()` and `msleep()`.

## Risks and Edge Cases

The map path does not check `qcomtee_mem_object_map()`'s return value and does not explicitly verify that `args[1].o` is a qcomtee memory object before mapping, so a malformed or unexpected callback object can make `container_of()` unsafe through the helper. Sleep trusts the input buffer value and may block the invoking path for a long time. Yield and sleep are QTEE-triggered scheduling behaviors in the context of the thread currently servicing secure world, so latency and signalability should be evaluated. Mapping cleanup relies on notify being called with an error if QTEE did not receive the response.

## Test Signals

Tests should cover exact argument signatures for all three ops, short input/output buffers, invalid op codes, forged non-memory objects for MAP_REGION, QTEE response failure after creating a mapping object, sleep durations including zero and large values, and callback-loop behavior when yield/sleep occurs during direct invocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/qcomtee/primordial_obj.c -->
