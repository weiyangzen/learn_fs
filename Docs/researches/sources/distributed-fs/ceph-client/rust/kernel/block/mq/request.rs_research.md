<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/block/mq/request.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/block/mq/request.rs

## Purpose
This file wraps blk-mq `struct request` and implements Rust-side reference accounting for in-flight block requests.

## Important APIs, Types, and Functions
`Request<T>` is a transparent wrapper over `bindings::request` plus type marker. Key methods are unsafe `aref_from_raw`, unsafe `start_unchecked`, private `try_set_end`, public `end_ok`, `complete`, unsafe `wrapper_ptr`, and `wrapper_ref`. `RequestDataWrapper` stores a `Refcount` in the request PDU and exposes `refcount` and unsafe `refcount_ptr`. `Request<T>` implements `Send`, `Sync`, and `AlwaysRefCounted`.

## Control Flow and State
When blk-mq queues a request, `operations.rs` sets refcount to `2`. `start_unchecked` calls `blk_mq_start_request` once Rust has exclusive request ownership. `end_ok` consumes an `ARef`, uses `try_set_end` to atomically change refcount from `2` to `0`, forgets the `ARef`, and calls `blk_mq_end_request`. If extra `ARef`s exist, it returns the request in `Err`. `complete` transfers an `ARef` raw pointer into blk-mq remote completion; if the C helper does not schedule remote completion, it reconstructs the `ARef` and calls the Rust complete callback immediately.

## State and Persistence Behavior
Refcount states encode ownership: `0` C-owned, `1` Rust-owned with no `ARef`, `2` Rust-owned with one `ARef`, and `>2` shared Rust references. The PDU wrapper persists for each request from `init_request` to `exit_request`. `AlwaysRefCounted::dec_ref` decrements the refcount and can panic under `CONFIG_DEBUG_MISC` if a Rust reference reaches zero unexpectedly.

## Dependencies and Integration Points
The module depends on blk-mq bindings, `ARef`, `AlwaysRefCounted`, `Refcount`, atomic `Relaxed`, and the `Operations` trait. It is called by operation callbacks and driver code that completes requests.

## Risks
The core risk is mismatched ownership between Rust references and C request lifetime. Ending requires exactly one live `ARef`; cloned references must be dropped first. `complete` deliberately leaks/reclaims raw references around C scheduling. Any driver that forgets to complete a request, holds a reference forever, or calls end twice can cause timeouts or refcount corruption.

## Test Signals
No direct tests are present. Runtime signals should include successful request completion, failure when ending with extra references, no debug refcount panic, and correct remote/local completion callback behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/block/mq/request.rs -->
