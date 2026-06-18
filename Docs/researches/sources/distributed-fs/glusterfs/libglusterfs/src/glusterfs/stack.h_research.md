# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/stack.h

Purpose: `stack.h` implements GlusterFS's async call-stack model: frames carry translator context, callback addresses, credentials, lock owner, latency timing, and error state while fops wind down and unwind up translator graphs.

Important APIs and types: `call_pool_t` owns all frames, counters, locks, and frame/stack mempools. `call_frame_t` stores root stack, parent, local data, cookie, `THIS`, return callback, fop index, completion, and trace names. `call_stack_t` stores credentials, pid, groups, client, operation, flags, timestamps, namespace info, and `gf_lkowner_t`. Key macros/functions include `STACK_WIND`, `STACK_WIND_COOKIE`, `STACK_WIND_TAIL`, `STACK_UNWIND_STRICT`, `FRAME_DESTROY`, `STACK_DESTROY`, `STACK_RESET`, `copy_frame`, `create_frame`, and group helpers.

Control flow and state: `STACK_WIND_COMMON` allocates a child frame, links it into the stack, switches global/thread `THIS`, records fop stats/latency, and calls the next translator fop. `STACK_UNWIND_STRICT` restores parent context, updates root error/err_xl, records callback stats, and invokes the typed callback. Destroy/reset paths remove frames under call-pool locks and free locals.

Dependencies and integration: tightly coupled to `xlator.h` fop table layout, `timespec.h`, memory pools, lock owner helpers, dict/client types, and logging. Syncop copies frames to present blocking APIs over this async machinery.

Risks: fop index calculation depends on exact `struct xlator_fops` order. A missing unwind leaks frames. `copy_frame()` must preserve credentials/groups/lkowner without sharing mutable arrays incorrectly. `FRAME_DESTROY` assumes frame-local allocations come from mempools. `THIS` switching is macro-heavy and fragile.

Test signals: translator fop wind/unwind tests, latency/stat counter assertions, error propagation through stacked translators, group allocation over/under `SMALL_GROUP_COUNT`, copied-frame credential preservation, and leak detection for failure paths are essential.
