# sources/distributed-fs/ceph-client/drivers/tee/optee/optee_private.h

## Purpose
`optee_private.h` is the internal OP-TEE driver contract. It defines common driver state, synchronization structures, transport-specific substructures, ops abstraction, session/context types, GP error constants, helper conversion functions, and prototypes shared by OP-TEE core, call, RPC, notification, protected-memory, and ABI backend code.

## Important APIs, Types, And Functions
`struct optee` is the central per-instance object. It owns client and supplicant `tee_device`s, selected `optee_ops`, internal context, an SMC or FF-A union, argument cache, call queue, notification database, supplicant queue, SHM pool, RPMB state, device-enumeration work, RPC parameter count, routing flags, and OS revision.

`struct optee_ops` abstracts transport differences: `do_call_with_arg()`, `to_msg_param()`, `from_msg_param()`, `lend_protmem()`, and `reclaim_protmem()`. `struct optee_call_queue`, `optee_call_waiter`, `optee_notif`, `optee_shm_arg_cache`, and `optee_supp` define persistent synchronization state. `struct optee_smc` carries SMCCC function pointer, reserved SHM mapping, capabilities, notification IRQ state, per-CPU notification work, and CPU hotplug state. `struct optee_ffa` carries FF-A device pointer, bottom-half notification id, global-id rhashtable, and notification workqueue.

Inline helpers convert value params and register pairs. Prototypes expose all common functions across files, including session operations, supplicant RPC, device enumeration, notifications, protected memory, RPC command helpers, ABI registration, and simple internal commands.

## Control Flow And State
The header expresses the main layering: backend probe creates and initializes `struct optee`; common TEE operations use `optee->ops`; client contexts use `optee_context_data` session lists; secure-world calls coordinate through `optee_call_queue`; RPC to userspace flows through `optee_supp`; async and synchronous notification state lives in `optee_notif`.

## Dependencies And Integration Points
It depends on ARM SMCCC, notifier chains, rhashtable, RPMB, semaphores, Linux TEE core, FF-A types via forward usage, and the OP-TEE message ABI. It is included by nearly every OP-TEE driver source in this subset.

## Risks
Because this file is a shared internal ABI, field lifetime assumptions must match all backends and common teardown. The union of `smc` and `ffa` means code must only touch the active transport fields. `optee_supp` supports both synchronous and asynchronous request modes; mixing them incorrectly is guarded in `supp.c` but can break userspace supplicant behavior.

## Test Signals
Build both SMC and FF-A backends, run probe/remove cycles, exercise supplicant connect/disconnect, run concurrent session calls, and test RPMB/notification/protected-memory optional capabilities to cover most shared state fields.
