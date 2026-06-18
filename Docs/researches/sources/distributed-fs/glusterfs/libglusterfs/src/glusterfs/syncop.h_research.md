# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/syncop.h

Purpose: `syncop.h` exposes synchronous/blocking wrappers over GlusterFS's asynchronous translator fops and defines the cooperative synctask scheduler used to implement blocking-style workflows.

Important APIs and types: `synctask`, `syncproc`, and `syncenv` implement user-context tasks, processor threads, run/wait queues, scheduler state, and stack sizing. `synclock`, `synccond`, and `syncbarrier` provide task-aware synchronization. `syncargs` stores common callback outputs and wait state. `syncopctx` carries override uid/gid/groups/pid/lkowner. APIs create/destroy/scale syncenvs, spawn/join/wake/yield/sleep tasks, set ids, initialize locks/conds/barriers, and perform many `syncop_*` filesystem operations.

Control flow and state: `SYNCOP` detects whether it runs inside a synctask. Inside a synctask it copies the current op frame; outside it creates a new frame and waits on pthread condition variables. It winds the async fop with `STACK_WIND_COOKIE`, yields or blocks until callback wakeup, then destroys the temporary stack. `syncop_create_frame` fills credentials/groups from `syncopctx` or process state.

Dependencies and integration: deeply depends on `stack.h`, `timer.h`, dict, iatt, iobuf, lock migration, and translator fop callback conventions. It bridges async translators to management/heal code that is easier to express synchronously.

Risks: scheduler state and ucontext stacks are delicate, especially with sanitizer integration. The header as read contains duplicated tokens (`else {` and duplicate `int`/prototype lines), indicating generated or source-quality hazards that builds/tests must catch. Errno decoding differs inside and outside synctasks. Callback wakeup must happen exactly once.

Test signals: build warnings, sanitizer runs, syncop success/error errno behavior, nested syncops, timeout/sleep/yield behavior, credential/group/lkowner propagation, barrier/lock semantics, and each fop wrapper's callback output ownership should be tested.
