<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/FuseServer/FusexCastBatch.hh -->
# sources/distributed-fs/eos/mgm/FuseServer/FusexCastBatch.hh

Purpose: Provides a tiny RAII batch for deferred FUSE broadcast callbacks, allowing code to register invalidation/update work and execute it at scope exit if not executed manually.

Important APIs/types/functions: `FusexCastBatch` stores `std::function<void()>` callbacks in `std::list`. `Register()` appends a callback, `Execute()` runs all callbacks in insertion order and clears the list, `GetSize()` returns pending callback count, and the destructor calls `Execute()` when callbacks remain. Copy and move operations are deleted.

Control flow: Callers create a batch, register lambdas while performing namespace or ACL/commit work, then either call `Execute()` explicitly or let the destructor execute the remaining callbacks. `Execute()` performs synchronous callback invocation on the caller's thread.

State and persistence behavior: State is only the pending callback list. There is no durable storage and no retry; once callbacks run or the process exits, state is gone.

Dependencies and integration points: Includes `mgm/Namespace.hh`, `<functional>`, and `<list>`. It is included by `XrdMgmOfs.hh/.cc`, `ofs/fsctl/CommitHelper.cc`, and user ACL command code. Commit helper registers broadcasts after successful filesystem changes so FUSE clients see the resulting metadata state.

Risks: Callbacks running from a destructor can throw during stack unwinding unless callers ensure lambdas are nonthrowing. The class is not thread-safe. Deleted move operations prevent returning or storing batches in many abstractions. Capturing references in delayed lambdas is risky if scope/lifetime assumptions change. Tests should cover manual execute clearing, destructor execution exactly once, callback order, and exception behavior policy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/FuseServer/FusexCastBatch.hh -->
