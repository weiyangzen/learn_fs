# sources/distributed-fs/lustre-release/lnet/selftest/selftest.h

## Purpose
Central internal header for LNet Selftest. It defines shared netlink attributes, workitem states, SRPC transport/service structures, framework session/test structures, inline helpers, and cross-file declarations.

## Important APIs And Types
Defines netlink attribute enums, `lsr_swi_state`, portal constants, `srpc_service2request()`, `srpc_service2reply()`, `srpc_event`, `srpc_bulk`, `srpc_buffer`, `swi_workitem`, `srpc_server_rpc`, `srpc_client_rpc`, `srpc_service_cd`, `srpc_service`, `lst_session_id`, `sfw_session`, `sfw_batch`, `sfw_test_client_ops`, `sfw_test_instance`, `sfw_test_unit`, and `sfw_test_case`.

## Control Flow
The header encodes the subsystem layering: SRPC services receive server RPCs, framework/test code creates client RPCs, workitems run on serial/test workqueues, and test client ops prepare and complete repeated test RPCs. `srpc_init_client_rpc()` is the core inline initializer.

## State And Persistence
Defines in-memory state only. Object lifetimes are controlled by krefs, refcounts, atomics, locks, and intrusive lists.

## Dependencies And Integration Points
Includes Linux/libcfs/LNet headers, UAPI selftest definitions, `rpc.h`, and `timer.h`. Exposes workqueues and APIs implemented by module, framework, RPC, timer, ping, and BRW files.

## Risks
Inline helper changes affect the whole subsystem. Variable-size RPC allocation depends on `srpc_client_rpc_size()`. New services require updates to service/message mapping. Workitem cancellation semantics are relied on during shutdown.

## Test Signals
Compile coverage, service-message mapping assertions, zero/nonzero bulk client RPC allocation, CPT workqueue scheduling, kref cleanup, and state string logging coverage.
