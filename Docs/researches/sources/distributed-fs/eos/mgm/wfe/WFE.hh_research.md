## sources/distributed-fs/eos/mgm/wfe/WFE.hh

Purpose: Declares the MGM workflow engine that executes asynchronous and synchronous workflow events, especially CTA/protobuf workflow actions and queue-backed policy processing. `WFE` owns the assisted engine thread, root virtual identity, an active-job counter, and a completion condition variable.

Important APIs and types: `WFE::Start`, `Stop`, and `WFEr` control the engine loop. `WFE::Job` extends `XrdJob` and carries `Action` records, file id, virtual identity, workflow path, retry count, and error text. Handler APIs cover `notify`, `proto`, prepare/abort/evict/create/delete/close/archived/offline/update-fid failure paths, `SendProtoWFRequest`, `EvictAsRoot`, `CollectAttributes`, and queue persistence methods `Save`, `Load`, `Move`, `Results`, and `Delete`.

Control flow: callers create `Job`, add one or more `Action`s, then either dispatch it through XRootD scheduling or invoke `DoIt` synchronously. `DoIt` delegates by method/event, records results, and moves jobs across queues, including retry handling. `Action` constructors derive string timestamps and day partitions used by persisted queue entries.

State and persistence: runtime state is `mActiveJobs`, `mDoneSignal`, `mThread`, and `gScheduler`; durable state is expressed through queue/day/action records managed by the `Job` persistence methods. Jobs include retry count and saved day to support moving between queued, running, retry, result, and delete states.

Dependencies and integration: integrates MGM namespace state, `VirtualIdentity`, file identifiers, `ThreadPool`/`AssistedThread`, XRootD job/scheduler/error types, CTA frontend protobuf requests, console reply protobufs, and global MGM services used in implementation. Workflow attributes from namespace metadata feed the engine through `Workflow`.

Risks: queue moves and retry behavior must remain idempotent, especially for external CTA events. `Job` copy construction omits `mVid` and `mWorkflowPath`, which is safe only if copies are not used for execution requiring those fields. Scheduler singleton lifetime and detached/asynchronous jobs require careful shutdown ordering. Proto opaque parsing must reject missing request ids without corrupting workflow state.

Test signals: cover sync and async workflow dispatch, queue save/load/move/delete, retry transitions, proto request construction, prepare idempotency, owner/user/group lookup, active-job publishing, and error propagation from each event handler.
