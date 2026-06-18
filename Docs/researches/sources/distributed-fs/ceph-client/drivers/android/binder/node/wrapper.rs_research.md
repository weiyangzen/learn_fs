# sources/distributed-fs/ceph-client/drivers/android/binder/node/wrapper.rs

Purpose: provides `CritIncrWrapper`, a small work-item wrapper used when a strong zero-to-one node refcount increment cannot be safely represented by scheduling the `Node` itself. It preserves Binder's requirement that critical acquire notifications reach the thread that caused them.

Important APIs/types/functions: `CritIncrWrapper::new` preallocates uninitialized storage for `DTRWrap<NodeWrapper>`. `CritIncrWrapper::init` pins a `NodeWrapper` around a `DArc<Node>` and returns it as `DLArc<dyn DeliverToRead>`. `NodeWrapper` implements `DeliverToRead` with `do_work`, `cancel`, `should_sync_wakeup`, and `debug_print`.

Control flow: `process.rs` allocates a wrapper after `Node::incr_refcount_allow_zero2one` reports `CouldNotDeliverCriticalIncrement`. On delivery, `NodeWrapper::do_work` locks the node owner process, asserts wrapper/strong-zero2one state, clears the wrapper scheduling flags, and delegates to `Node::do_work_locked` to write the actual Binder return commands.

State and persistence: the wrapper owns only an arc to the target node and exists while queued on a thread or process work list. Persistent scheduling state remains in `NodeInner.delivery_state`; the wrapper is the transport used to disambiguate one pending strong increment from other node work.

Dependencies and integration points: depends on `node.rs` private delivery-state access, `Thread`, `BinderReturnWriter`, `DTRWrap`, `ListArc`, and `UniqueArc`. It is intentionally internal to the `node` module and exported as `CritIncrWrapper`.

Risks: the asserts in `do_work` encode critical invariants; a wrapper queued without `has_pushed_wrapper` and `has_strong_zero2one` indicates corrupted scheduling state. If wrapper allocation fails, the higher-level refcount path returns allocation failure to avoid losing a required acquire notification.

Test signals: force concurrent weak and strong zero-to-one increments so the normal node delivery path is already occupied, then verify a wrapper is used and `BR_ACQUIRE` reaches the initiating thread. Invalid double scheduling should surface as assertion or warning failures in debug builds.
