<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/qcomtee/qcomtee.h -->
# sources/distributed-fs/ceph-client/drivers/tee/qcomtee/qcomtee.h

## Purpose

`qcomtee.h` is the internal umbrella header for the Qualcomm QTEE driver. It collects the transport/message and object headers, defines OBJREF flag semantics, declares the main driver and per-context state structures, and exposes cross-file APIs for shared memory, object invocation, user objects, primordial services, and memory objects.

## Important APIs, Types, and Functions

OBJREF flags distinguish QTEE-hosted objects (`QCOMTEE_OBJREF_FLAG_TEE`), userspace callback objects (`QCOMTEE_OBJREF_FLAG_USER`), and memory objects (`QCOMTEE_OBJREF_FLAG_MEM`). `struct qcomtee` holds the registered `tee_device`, shared-memory pool, private async context, reusable invocation context, ordered workqueue, local-object xarray, cyclic ID cursor, and cached version. `struct qcomtee_context_data` holds each open file/context's QTEE object IDR, supplicant request IDR/list, locks, completion, and release state.

The header declares conversion functions for context object mappings and OBJREFs, the internal object invocation entry point, message buffer allocation/free functions, asynchronous request helpers, QTEE shared-memory pool allocation, user-object request select/submit functions, and memory-object map/conversion helpers.

## Control Flow

The declarations reflect the cross-file pipeline: `call.c` receives generic TEE params and uses OBJREF converters; `core.c` marshals objects and messages and calls buffer allocation in `shm.c`; callback dispatch may enter `user_obj.c`, `primordial_obj.c`, or `mem_obj.c`; asynchronous releases use `qcomtee_fetch_async_reqs()` and `qcomtee_idx_erase()` to reconcile secure-world object references with the local xarray.

## State and Persistence Behavior

This header owns no storage, but it defines the state layout for the driver and per-context lifetimes. The state is strictly runtime: open contexts, IDR/xarray mappings, pending requests, completion waiters, shared-memory buffers, and secure-world object handles. There is no file-backed persistence.

## Dependencies and Integration Points

`qcomtee.h` depends on Linux kobject/TEE core definitions and the local `qcomtee_msg.h` and `qcomtee_object.h`. Its declarations are used across every qcomtee `.c` file and by the platform driver's TEE registration. It also creates the contract between QTEE-specific OBJREF flags and the generic TEE ioctl parameter model.

## Risks and Edge Cases

Because ownership rules are mostly documented across function comments instead of encoded in types, it is easy for callers to miss required gets/puts for objects or contexts. The `qcomtee` struct contains a reusable `oic` for async releases, so callers must serialize work through the ordered workqueue as implemented. `struct qcomtee_context_data.released` is protected by `reqs_lock`; any future direct access without the lock would race with supplicant teardown.

## Test Signals

Static checks should verify every declaration is implemented and that qcomtee files include this header rather than duplicating contracts. Runtime tests should stress object/context reference counts, local-object xarray allocation bounds, supplicant queue locking, and the three OBJREF flag classes through both normal and failure conversion paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/qcomtee/qcomtee.h -->
