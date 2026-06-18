# sources/distributed-fs/ceph/src/osdc/SplitOp.h

## Purpose

`SplitOp.h` declares the split-read abstraction used by `Objecter` to parallelize eligible client reads across multiple OSDs. It defines shared bookkeeping for sub-reads, EC stripe iteration, result assembly contracts, torn-read protection, and the concrete EC and replicated-pool specializations.

## Important APIs, types, and functions

`SplitOp` defines `extent`, `extents_map`, and `extent_set` aliases for read ranges. `ECChunkInfo`, `ECStripeIterator`, and `ECStripeView` model logical-to-shard traversal for erasure-coded stripes. The iterator reports logical object offset, shard offset, chunk length, and raw shard id for each chunk and is asserted to satisfy `std::input_iterator`.

`Details` stores one sub-operation's response buffer, return value, error code, and optional sparse extent map. `InternalVersion` stores the reply from `CEPH_OSD_OP_GET_INTERNAL_VERSIONS`. `SubRead` owns the child `ObjectOperation`, response details by original op index, a sub-op return code, and optional version data. `Finisher` is the child completion context that records the return code while retaining the parent split op.

`SplitOp` declares virtual assembly and initialization hooks: `assemble_buffer_sparse_read()`, `assemble_buffer_read()`, `init_read()`, `version_mismatch()`, and `init_reference_sub_read()`. Public APIs are `complete()`, `prepare_single_op()`, `protect_torn_reads()`, and static `create()`.

`ECSplitOp` implements shard-aware EC assembly and version comparison. `ReplicaSplitOp` implements replica chunking and assembly, with a constructor that sizes sub-read storage from pool size.

## Control flow

The header establishes a staged lifecycle. `create()` validates an `Objecter::Op`, constructs the right subclass, initializes the reference sub-read, calls `init()` for each original OSD op, protects torn reads by appending version checks, and submits child reads. `init()` dispatches reads and sparse reads to `init_read()` while primary-only supported ops pass through to the reference sub-read. When the last child completion releases its `shared_ptr`, the derived destructor invokes `complete()`, which assembles replies and informs `Objecter`.

## State and persistence behavior

`SplitOp` state is entirely in-memory and bound to one parent operation. It holds the original op pointer, `Objecter` reference, sub-read map, abort flag, flags, reference sub-read index, and an unused-looking `op_offset_map`. The state is not durable; consistency is maintained by comparing OSD internal versions and falling back to a retry if torn reads are detected.

## Dependencies and integration points

The header includes `Objecter.h`, Ceph buffer and interval-set types, pool/EC types, `mini_flat_map`, locks, and Boost error codes. It is intentionally close to `Objecter`: the split classes are friends of `Objecter`, and the implementation calls private objecter methods. It also depends on EC pool geometry from `pg_pool_t` and OSD op codes such as read, sparse read, and get-internal-versions.

## Risks and edge cases

`ECStripeIterator::operator!=()` only compares current length because it is used as a sentinel-driven range; this is valid for the local loop style but not a general-purpose iterator equality model. The pre-increment expression updates `shard_offset` by `current_info.length - chunk_size`, which relies on unsigned arithmetic and later wrap logic; EC boundary tests are important. `Finisher` uses a legacy self-destructing `Context` pattern, so ownership assumptions must match Ceph's completion semantics. Derived destructors calling `complete()` make the `abort` flag a correctness guard against fallback paths accidentally completing.

## Test signals

Header-level behavior should be tested through `SplitOp.cc` integration: EC stripe iteration across chunk boundaries, sparse and dense assembly, mixed read/metadata ops, torn-read version checks, fallback when sub-read count is one, and parent/child lifetime under cancellation or error.
