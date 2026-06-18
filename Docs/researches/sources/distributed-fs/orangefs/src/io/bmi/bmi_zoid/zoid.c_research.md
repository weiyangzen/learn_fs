# sources/distributed-fs/orangefs/src/io/bmi/bmi_zoid/zoid.c

## Purpose
Implements the OrangeFS BMI method named `bmi_zoid`, targeting ZOID-based Blue Gene style compute-node to I/O-node communication. It provides the BMI method-ops table, client-side send/receive/test/cancel behavior, and delegates server-side behavior to `server.c` helpers declared in `zoid.h`.

## Important APIs, Types, And Functions
The file exports `bmi_zoid_ops` and the global `zoid_method_id`. Core helpers are `zoid_post_send_common`, `zoid_post_recv_common`, `zoid_test_common`, and `zoid_err_to_bmi`. BMI callbacks include `BMI_zoid_initialize`, `finalize`, `set_info`, `get_info`, `memalloc`, `memfree`, `unexpected_free`, `post_send`, `post_sendunexpected`, `post_recv`, `test`, `testsome`, `testcontext`, `testunexpected`, `method_addr_lookup`, list send/recv variants, context open/close, `cancel`, and `rev_lookup_unexpected`.

## Control Flow
Initialization records whether the process is a BMI server or client, stores the method id, allocates a pending `op_list`, and either calls `__zoid_init()` for clients or `BMI_zoid_server_initialize()` for servers. Client sends and receives first try immediate ZOID calls (`zbmi_send`, `zbmi_recv`). If a client send fails with `ENOMEM`, the operation is converted to a queued `method_op`; client receives are queued when no matching send is ready. `zoid_test_common` asks ZOID which queued operations are ready, completes matching sends/receives, handles canceled operations, fills BMI completion arrays, removes finished ops from `zoid_ops`, and deallocates the method ops. Server paths are thin pass-throughs to `zoid_server_*` helpers.

## State And Persistence
State is process-local: `zoid_node_type`, `zoid_method_id`, a static `zoid_ops` pending-op queue, and a cached singleton method address for `zoid://`. No disk persistence exists. The client side supports only the server address, one global BMI context, no compute-node to compute-node traffic, and no client-side multithreading. Pending op `method_data` is reused as a boolean that marks unexpected sends.

## Dependencies And Integration Points
This file integrates BMI method support (`bmi-method-support.h`, `method_op` allocation), `id-generator`, `op-list`, ZOID APIs (`zbmi.h`, `zoid_api.h`), and the server-side `bmi_zoid` implementation. It is selected through the BMI method table and must match BMI core expectations for operation ids, completion arrays, memory allocation, cancellation, max-size queries, and address cleanup.

## Risks And Test Signals
Risks include hard limits of 128 MiB expected and 8 KiB unexpected messages, aborts for unsupported client/server directions, `alloca` use proportional to list and test counts, single cached address lifetime, no real context isolation, and assumptions that `id_gen_fast_lookup` always returns a valid op for cancellation/test. Tests should cover immediate and deferred sends/receives, unexpected client-to-server messages, oversize rejection, `ENOMEM` retry behavior, cancellation completions, `testcontext` enumeration, server delegation, and `BMI_DROP_ADDR`.
