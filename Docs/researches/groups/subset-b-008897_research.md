# subset-b-008897 Research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_expr/src/types/expr_builder.rs -->
# sources/storage-engines/tikv/components/tidb_query_expr/src/types/expr_builder.rs

## Purpose
This file converts TiDB protobuf expression trees (`tipb::Expr`) into `RpnExpression` node lists used by the batch expression evaluator. It is the validation and lowering bridge between TiDB request expressions and TiKV's typed RPN runtime. The builder performs supported-expression screening, field-type to `EvalType` checks, postorder traversal, function metadata binding, column-offset validation, and constant decoding.

## Important APIs, Types, and Control Flow
`RpnExpressionBuilder` is a thin `Vec<RpnExpressionNode>` wrapper with production entry points `check_expr_tree_supported`, `is_expr_eval_to_scalar`, and `build_from_expr_tree`. Test-only helpers construct constants, column refs, and function calls directly. `append_rpn_nodes_recursively` is the main lowering routine: scalar functions are handled by `handle_node_fn_call`, column references by `handle_node_column_ref`, and all other supported literal nodes by `handle_node_constant`. Function calls are mapped through `map_expr_node_to_rpn_func`, validated through the macro-generated validator, given optional metadata through `metadata_expr_ptr`, then children are recursively appended before the function node is pushed.

Constant decoding maps protobuf expression types plus `FieldType` into `ScalarValue`: integers, unsigned integers, bytes, reals, MySQL time/duration/decimal/json/enum/bit, nulls, and TiDB vector-float32 values. Time decoding uses `EvalContext` and field decimal precision, while enum/json/vector decoding delegates to datatype codecs.

## State, Dependencies, and Integration
The builder consumes `Expr` values by taking child lists, values, and field types. It does not persist state beyond the produced `RpnExpression`. Its correctness depends on `tidb_query_datatype` codecs, protobuf field metadata, TiDB expression signatures, and the function registry. `max_columns` is a schema-size guard for column refs, not a complete schema validator.

## Risks and Test Signals
Risks center on mismatched `ExprType` and `EvalType`, unchecked casts from unsigned values to signed ints, recursive depth, and stale assumptions in `check_expr_tree_supported` about provided eval types. Tests cover validator behavior for fixed, variadic, and raw variadic functions; postorder conversion; column bounds; and bit literal decoding.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_expr/src/types/expr_builder.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_expr/src/types/expr_eval.rs -->
# sources/storage-engines/tikv/components/tidb_query_expr/src/types/expr_eval.rs

## Purpose
This file evaluates an `RpnExpression` against batch input columns and logical row indexes. It defines the stack representation used while walking RPN nodes and implements `RpnExpression::eval`, including lazy column decoding, stack manipulation, scalar/vector argument handling, and vector result production.

## Important APIs, Types, and Control Flow
`RpnStackNodeVectorValue` represents vector values as either generated owned `VectorValue` results or references to decoded input columns plus logical rows. `take_vector_value` materializes references into compact owned vectors by copying selected logical rows. `RpnStackNode` wraps either scalar constants with their `FieldType` or vector nodes with their field type.

`RpnExpression::eval` first calls `ensure_columns_decoded` for every `ColumnRef`, passing schema field types and logical rows into `LazyBatchColumnVec`. It then calls `eval_decoded`, which asserts a nonzero output size at or below `BATCH_MAX_SIZE`, pushes constants and column refs onto a stack, and invokes each function node by slicing the last `args_len` stack entries. The function pointer stored in `RpnFnMeta` receives `EvalContext`, output row count, argument nodes, return field type through `RpnFnCallExtra`, and metadata. The returned `VectorValue` replaces its arguments on the stack.

## State, Dependencies, and Integration
Evaluation mutates only the evaluation context and lazy input columns during decode. Generated vector results live on the stack; referenced columns borrow from caller-owned input. Logical row state is explicit, allowing filtered or reordered rows without reshaping physical columns. Integration points include `tidb_query_codegen::rpn_fn` generated evaluators, `LazyBatchColumnVec`, `VectorValue`, `FieldType`, and expression nodes built by `expr_builder.rs`.

## Risks and Test Signals
The evaluator intentionally panics for structurally invalid RPN, decoded-column mismatches, invalid output row counts, and wrong eval types. Borrowing and logical-row handling are key correctness risks. Tests cover constants, decoded and raw columns, scalar/vector argument combinations, null propagation, parsed tree evaluation, function metadata, `take_vector_value`, invalid expressions, and microbenchmarks for arithmetic, comparison, real, and bytes paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_expr/src/types/expr_eval.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_expr/src/types/function.rs -->
# sources/storage-engines/tikv/components/tidb_query_expr/src/types/function.rs

## Purpose
This file defines the runtime ABI for RPN scalar functions generated by the `tidb_query_codegen::rpn_fn` procedural macro. It lets regular Rust functions become validated, metadata-aware, batch evaluators over `RpnStackNode` arguments.

## Important APIs, Types, and Control Flow
`RpnFnMeta` stores the function name, expression validator, metadata constructor, and callable function pointer. `RpnFnCallExtra` carries return field type. `RpnFnArg` abstracts row-wise access for scalar and vector arguments and exposes null bitmaps for optimized evaluators. `ScalarArg` returns one optional value for every row; `VectorArg` maps logical rows into physical column references.

`ArgDef`, `Arg`, and `Null` form a type-level linked list of arguments. `Evaluator` is the trait used by generated code: `ArgConstructor` inspects `RpnStackNode` at an argument index, builds a scalar or vector argument wrapper of the expected `EvaluableRef` type, prepends it to the argument definition, then delegates to the inner evaluator. Validation helpers enforce return eval type and argument count constraints, including exact, lower-bound, and upper-bound arity.

## State, Dependencies, and Integration
The file depends on `tidb_query_datatype` eval/ref traits, `EvalContext`, `FieldType`, and protobuf expressions. It also owns thread-local buffers used by generated variadic and raw variadic functions to reduce allocation overhead. `extract_metadata_from_val` decodes protobuf metadata from expression values, supplying default metadata for empty values.

## Risks and Test Signals
Safety depends on generated code passing compatible `EvaluableRef` types and correctly managing thread-local buffers. Return validation intentionally allows enum-as-int and enum-as-bytes compatibility. The strongest tests live in `expr_eval.rs` and `expr_builder.rs`, where generated macro functions exercise metadata capture, variadic argument validation, null handling, and eval type mismatch panics.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_expr/src/types/function.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_expr/src/types/mod.rs -->
# sources/storage-engines/tikv/components/tidb_query_expr/src/types/mod.rs

## Purpose
This module is the public facade for the `tidb_query_expr::types` submodule. It wires together the internal RPN expression representation, builder, evaluator stack node, function metadata ABI, and test utilities.

## Important APIs, Types, and Control Flow
The file declares private modules `expr`, `expr_builder`, and `expr_eval`, a public `function` module, and a test-only `test_util` module. It re-exports `RpnExpression`, `RpnExpressionNode`, `RpnExpressionBuilder`, `BATCH_MAX_SIZE`, `RpnStackNode`, `RpnFnCallExtra`, and `RpnFnMeta`. There is no runtime control flow in this file; it controls namespace boundaries and which internals are available to the rest of the crate.

## State, Dependencies, and Integration
This facade is used by expression implementation modules and tests that need to build or evaluate RPN expressions without depending on internal filenames. It keeps the evaluator's `RpnStackNode` visible for generated function glue while keeping helper modules mostly private.

## Risks and Test Signals
The main risk is API surface drift: making internals too private can break generated code or tests, while exporting too much can freeze implementation details. Test signals are indirect through all expression builder, evaluator, and RPN function tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_expr/src/types/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_expr/src/types/test_util.rs -->
# sources/storage-engines/tikv/components/tidb_query_expr/src/types/test_util.rs

## Purpose
This file provides `RpnFnScalarEvaluator`, a test helper for evaluating one RPN scalar function over scalar constants without constructing full batch columns manually. It is intentionally test-oriented and trades efficiency for ergonomic function tests.

## Important APIs, Types, and Control Flow
`RpnFnScalarEvaluator` accumulates parameters with `RpnExpressionBuilder`, optional return field type, optional `EvalContext`, and optional function metadata. `push_param`, `push_params`, and `push_param_with_field_type` add constant nodes. `return_field_type`, `context`, and `metadata` configure evaluation. `evaluate_raw` builds child expression descriptors from accumulated RPN nodes, constructs a scalar-function expression with a requested `ScalarFuncSig`, maps it through the real function registry, validates arguments, prepares metadata if not provided, pushes the function call, evaluates one output row, and returns the first scalar result plus the final context. `evaluate<T>` infers the return field type from `EvaluableRet` and converts `ScalarValue` into `Option<T>`.

## State, Dependencies, and Integration
The helper uses production `RpnExpressionBuilder`, `map_expr_node_to_rpn_func`, and `expr.eval`, so tests exercise the same validator, metadata, and function-pointer path as real evaluation. It integrates with `LazyBatchColumnVec::empty` because all inputs are scalar constants.

## Risks and Test Signals
The helper builds synthetic protobuf child descriptors, so it can miss issues that depend on real column refs, lazy decoding, or logical rows. It also deliberately ignores previously configured `return_field_type` in `evaluate_raw`. Its value is high for scalar function unit tests because validation failures and context mutations are surfaced directly.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_expr/src/types/test_util.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_alloc/Cargo.toml -->
# sources/storage-engines/tikv/components/tikv_alloc/Cargo.toml

## Purpose
This manifest defines the `tikv_alloc` crate, the workspace component responsible for installing and abstracting TiKV's global allocator. It exposes feature-controlled allocator backends and jemalloc profiling support.

## Important APIs, Types, and Control Flow
The primary feature is `jemalloc`, which pulls in `tikv-jemallocator`, `tikv-jemalloc-ctl`, and `tikv-jemalloc-sys`. `mem-profiling` enables jemallocator profiling support. Optional allocator alternatives are `mimalloc`, `snmalloc`, and `tcmalloc`, with tcmalloc built from bundled sources. Dependencies include `fxhash` for memory trace maps, `lazy_static` for jemalloc global maps, and `libc` for FFI.

## State, Dependencies, and Integration
The crate is unpublished and Rust 2021. It participates in workspace linting and explicitly allows the custom `cfg(fuzzing)` in `unexpected_cfgs`. Downstream binaries link to this crate to select the allocator at compile time. Feature combinations are resolved in `src/lib.rs` through cfg-selected `imp` modules.

## Risks and Test Signals
Risks include mutually enabled allocator features creating multiple `imp` modules on Unix, backend-specific platform limits, and profiling functions only working when both Cargo features and runtime jemalloc config are correct. The manifest's dev dependency on `tempfile` supports profiling dump tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_alloc/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_alloc/src/default.rs -->
# sources/storage-engines/tikv/components/tikv_alloc/src/default.rs

## Purpose
This file supplies no-op allocator observability and profiling functions for backends that do not implement jemalloc-specific behavior. It is re-exported by system, mimalloc, snmalloc, and tcmalloc implementations.

## Important APIs, Types, and Control Flow
`dump_stats` returns an empty string, `fetch_stats` returns `Ok(None)`, profiling control functions return `ProfError::MemProfilingNotEnabled`, arena count is zero, profiling activity is false, and thread allocation-stat callbacks do nothing. `thread_allocate_exclusive_arena` returns success because non-jemalloc backends do not need arena setup. The unsafe `add_thread_memory_accessor` is intentionally harmless to match the jemalloc API shape.

## State, Dependencies, and Integration
There is no persistent state. The module depends only on `ProfError`, `ProfResult`, and `AllocStats`. It allows the public `tikv_alloc` API to remain stable regardless of selected allocator.

## Risks and Test Signals
The main risk is silent loss of observability when a non-jemalloc backend is selected: callers must handle `None`, empty strings, or profiling-not-enabled errors. This behavior is deliberate and keeps non-jemalloc builds simple.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_alloc/src/default.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_alloc/src/error.rs -->
# sources/storage-engines/tikv/components/tikv_alloc/src/error.rs

## Purpose
This file defines the error type used by allocator profiling and control APIs.

## Important APIs, Types, and Control Flow
`ProfError` distinguishes disabled profiling, I/O errors, jemalloc control errors, non-Unicode dump paths, and paths containing NUL bytes. `ProfResult<T>` is the crate-local result alias. `Display` formats user-facing messages, and `From<std::io::Error>` plus `From<std::ffi::NulError>` make filesystem and CString conversion failures flow into allocator APIs.

## State, Dependencies, and Integration
The type is stateless and shared by `default.rs`, `jemalloc.rs`, and public callers through `tikv_alloc::error`. Profiling dump code uses it when converting paths and when jemalloc mallctl calls fail.

## Risks and Test Signals
The error messages are simple and not structured with source chains beyond implementing `std::error::Error`. Consumers that need exact jemalloc failure classes only receive strings. Tests are indirect through profiling tests and no-op backend behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_alloc/src/error.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_alloc/src/jemalloc.rs -->
# sources/storage-engines/tikv/components/tikv_alloc/src/jemalloc.rs

## Purpose
This file is the full jemalloc-backed implementation of `tikv_alloc`. It installs `tikv_jemallocator::Jemalloc`, exposes allocator stats, supports optional heap profiling, tracks per-thread allocation counters, and optionally maps threads to exclusive jemalloc arenas.

## Important APIs, Types, and Control Flow
`Allocator` aliases `tikv_jemallocator::Jemalloc`. Global maps track thread memory accessors and thread-to-arena mappings. `PeekableRemoteStat<T>` wraps raw jemalloc thread-local statistic pointers and reads them atomically; `MemoryStatsAccessor` records allocated/deallocated pointers plus thread name. `add_thread_memory_accessor` registers the current thread, and `remove_thread_memory_accessor` removes both memory and arena state.

`dump_stats` calls `malloc_stats_print`, then appends per-thread allocation data. `fetch_stats` advances the jemalloc epoch and returns allocated, active, metadata, resident, mapped, retained, dirty, and fragmentation values. `iterate_thread_allocation_stats` trims thread-pool numeric suffixes and aggregates by logical thread name. `iterate_arena_allocation_stats` deduplicates `(thread_name, arena)` pairs before reading resident, mapped, and retained arena stats.

With `mem-profiling`, the nested `profiling` module controls `prof.active`, `prof.dump`, `prof.reset`, background threads, arena creation, `thread.arena`, and profiling sample rate. Without that feature, profiling APIs return disabled errors or no-op values.

## State, Dependencies, and Integration
State is process-global behind mutexes and jemalloc mallctl state. Safety depends on registered threads calling `remove_thread_memory_accessor` before exit because remote TLS pointers can otherwise dangle. Integration points include `tikv_jemalloc_ctl`, `tikv_jemalloc_sys`, thread wrappers, metrics collectors, and profiling tools.

## Risks and Test Signals
Key risks are unsafe remote TLS reads, stale map entries, feature/runtime mismatch for profiling, unwraps in stats paths, and arena accounting skew if thread names or arena reuse are unexpected. Tests cover non-empty stats dumps, approximate allocation/deallocation counters, arena-map cleanup, deduplication for same arena, and ignored profiling dump/activation cases gated by `MALLOC_CONF`.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_alloc/src/jemalloc.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_alloc/src/lib.rs -->
# sources/storage-engines/tikv/components/tikv_alloc/src/lib.rs

## Purpose
This is the root of the allocator crate. It documents allocator policy, selects one backend implementation with cfg gates, re-exports the public allocator/stat/profiling API, and installs the selected global allocator.

## Important APIs, Types, and Control Flow
The crate enables nightly test features and `core_intrinsics`. `AllocStats` is `Vec<(&'static str, usize)>`. `error` and `trace` are public modules. The `imp` module is selected from `jemalloc.rs`, `tcmalloc.rs`, `mimalloc.rs`, `snmalloc.rs`, or `system.rs` depending on Unix, `fuzzing`, and feature flags. `pub use crate::{imp::*, trace::*}` exposes backend functions and memory tracing. `#[global_allocator] static ALLOC: imp::Allocator = imp::allocator();` installs the selected allocator.

The test-only `runner` enables ignored tests with messages prefixed by `#ifdef <VAR_NAME>` when the environment variable is present, which is used for profiling tests requiring `MALLOC_CONF`.

## State, Dependencies, and Integration
Linking this crate transitively causes TiKV binaries and tests to use the production allocator where supported. The crate intentionally centralizes jemalloc-specific code and presents stable functions even when selected backends are no-op for profiling.

## Risks and Test Signals
Feature selection is the biggest risk. The cfg layout can define multiple `imp` modules if multiple allocator features are enabled simultaneously on Unix; normal workspace configuration must avoid that. Fuzzing disables custom Unix allocators and falls back to system. Tests are backend-specific and routed through the custom runner.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_alloc/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_alloc/src/mimalloc.rs -->
# sources/storage-engines/tikv/components/tikv_alloc/src/mimalloc.rs

## Purpose
This file selects mimalloc as the global allocator backend while reusing the default no-op observability implementation.

## Important APIs, Types, and Control Flow
It re-exports `crate::default::*`, aliases `Allocator` to `mimalloc::MiMalloc`, and returns `mimalloc::MiMalloc` from `allocator()`. There is no additional control flow.

## State, Dependencies, and Integration
The backend is compiled when the `mimalloc` feature and Unix allocator cfg select it in `lib.rs`. Profiling, stats, thread accounting, and arena APIs behave like `default.rs`.

## Risks and Test Signals
The risk is that allocator replacement succeeds while TiKV-specific memory stats become unavailable. Tests would be primarily compile/link tests plus shared no-op API behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_alloc/src/mimalloc.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_alloc/src/snmalloc.rs -->
# sources/storage-engines/tikv/components/tikv_alloc/src/snmalloc.rs

## Purpose
This file selects snmalloc as the global allocator backend while reusing default allocator API fallbacks.

## Important APIs, Types, and Control Flow
It re-exports `crate::default::*`, aliases `Allocator` to `snmalloc_rs::SnMalloc`, and returns that allocator from `allocator()`. There is no runtime logic beyond allocator construction.

## State, Dependencies, and Integration
The backend is selected by the `snmalloc` feature under the cfg rules in `lib.rs`. It keeps the public API compatible with jemalloc builds but does not provide profiling or detailed stats.

## Risks and Test Signals
Operational tooling expecting jemalloc stats will receive no-op values. The main validation signal is successful feature build and global allocator installation.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_alloc/src/snmalloc.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_alloc/src/system.rs -->
# sources/storage-engines/tikv/components/tikv_alloc/src/system.rs

## Purpose
This file selects Rust's system allocator backend and reuses the default no-op profiling/stat API.

## Important APIs, Types, and Control Flow
It re-exports `crate::default::*`, aliases `Allocator` to `std::alloc::System`, and returns `std::alloc::System` from `allocator()`.

## State, Dependencies, and Integration
This backend is used when custom allocator cfgs do not apply, including non-Unix and fuzzing builds. It preserves the same public functions as other backends.

## Risks and Test Signals
System allocator behavior varies by platform, and RocksDB/C malloc replacement may differ from jemalloc builds. Memory profiling and allocator stats are unavailable through this crate in this mode.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_alloc/src/system.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_alloc/src/tcmalloc.rs -->
# sources/storage-engines/tikv/components/tikv_alloc/src/tcmalloc.rs

## Purpose
This file selects tcmalloc as the global allocator backend while reusing default allocator observability fallbacks.

## Important APIs, Types, and Control Flow
It re-exports `crate::default::*`, aliases `Allocator` to `tcmalloc::TCMalloc`, and returns `tcmalloc::TCMalloc` from `allocator()`. There is no extra runtime control flow.

## State, Dependencies, and Integration
The backend is selected by the `tcmalloc` feature and uses the bundled tcmalloc dependency declared in the manifest. Public stats and profiling functions are the no-op defaults.

## Risks and Test Signals
The crate does not surface tcmalloc-specific statistics, so callers expecting jemalloc-like introspection must tolerate disabled profiling and absent stats. Build/link success is the primary backend signal.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_alloc/src/tcmalloc.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_alloc/src/trace.rs -->
# sources/storage-engines/tikv/components/tikv_alloc/src/trace.rs

## Purpose
This module implements logical memory tracing as a tree of named or numeric nodes. It is independent of the global allocator backend and lets components attribute memory usage to logical subsystems rather than stack traces.

## Important APIs, Types, and Control Flow
`Id` identifies trace nodes by static name or number and provides raw and readable names. `TraceEvent` represents additive, subtractive, or reset updates and implements combination semantics where later reset events dominate. `MemoryTrace` stores an id, atomic local trace value, and child map keyed by `Id`. It can record events, create RAII guards, snapshot the tree, access subtraces, add children, compute recursive sums, and list child ids.

The exported `mem_trace!` macro constructs an `Arc<MemoryTrace>` tree from nested syntax. `MemoryTraceGuard<T>` increments a trace on creation and decrements on drop or `consume`; it derefs to the wrapped item and can map to a new wrapped type while preserving accounting.

## State, Dependencies, and Integration
Trace values are in-memory atomics with relaxed ordering. Children are immutable after setup in common use, built through `Arc::get_mut` during macro construction. The module uses `fxhash` for faster maps and is re-exported from `tikv_alloc::lib`.

## Risks and Test Signals
Risks include underflow if subtract events exceed current trace, panics on missing `sub_trace`, and stale snapshots under concurrent updates. `MemoryTraceGuard` requires `T: Default` because it moves values out via `mem::take`. Tests cover id formatting, readable names, macro tree construction and sum behavior, and `TraceEvent` combination rules.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_alloc/src/trace.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_kv/Cargo.toml -->
# sources/storage-engines/tikv/components/tikv_kv/Cargo.toml

## Purpose
This manifest defines `tikv_kv`, the key-value abstraction layer directly used by TiKV. It ties together engine traits, raftstore test engines, RocksDB engine support, transaction key types, metrics, logging, and async primitives.

## Important APIs, Types, and Control Flow
Default features enable RocksDB KV test engine and raft-engine raft test engine through `raftstore`. Additional feature flags select RocksDB test engines, panic engines, or failpoints. Runtime dependencies include `engine_traits`, `engine_rocks`, `engine_panic`, `raftstore`, `kvproto`, `txn_types`, `futures`, `prometheus`, `tikv_util`, and logging/error crates.

## State, Dependencies, and Integration
This crate sits between TiKV's storage logic and concrete engine implementations. The manifest shows integration with raftstore, PD client, filesystem abstractions, and metrics, indicating that code in this crate must remain generic over snapshot and iterator traits while supporting real RocksDB and test engines.

## Risks and Test Signals
Feature combinations determine which engines are available for tests. Failpoint support is optional. Dev dependencies on `keys` and `panic_hook` support cursor and engine behavior tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_kv/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_kv/src/btree_engine.rs -->
# sources/storage-engines/tikv/components/tikv_kv/src/btree_engine.rs

## Purpose
This file implements `BTreeEngine`, an in-memory `BTreeMap`-based engine used for tests and benchmarks. It mimics enough of TiKV's engine, snapshot, and iterator interfaces to run common KV tests without RocksDB.

## Important APIs, Types, and Control Flow
`BTreeEngine` owns ordered column-family names and `Arc<RwLock<BTreeMap<Key, Value>>>` contents. `new` ensures a default CF exists, and `get_cf` resolves CF name to the shared tree. The `Engine` implementation supports `async_write` by applying `Modify` values and returning a single `WriteEvent::Finished`, rejects empty writes, and returns fake snapshots through `async_snapshot` and `async_in_memory_snapshot`. `kv_engine` and `modify_on_kv_engine` are unimplemented because this is not a full local engine wrapper.

`BTreeEngineIterator` tracks the current cloned key/value, validity flag, tree reference, and bounds derived from `IterOptions`. Seek operations translate to `BTreeMap::range` over included/excluded bounds and choose either the first or last endpoint. `Snapshot` reads clone values from the underlying shared map and creates iterators.

## State, Dependencies, and Integration
All state is in memory and protected by `RwLock`. Snapshots are explicitly not isolated: they clone the engine handles, so later writes affect snapshot reads. `write_modifies` supports put, delete, and pessimistic lock writes to `CF_LOCK`; range delete and ingest are unimplemented.

## Risks and Test Signals
This engine is unsuitable for persistence, isolation, range deletion, ingestion, or exact RocksDB behavior. Iterator methods panic if key/value are read while invalid. Tests cover base CRUD, linear scans, CF statistics, iterator bounds, forward/backward movement, and panic on missing CF.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_kv/src/btree_engine.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_kv/src/cursor.rs -->
# sources/storage-engines/tikv/components/tikv_kv/src/cursor.rs

## Purpose
This file defines `Cursor`, TiKV's higher-level wrapper around engine iterators. It adds scan-mode semantics, near-seek optimization, prefix-seek handling, key/value read accounting, iterator error handling, and a builder for snapshot cursors.

## Important APIs, Types, and Control Flow
`Cursor<I>` stores an engine iterator, `ScanMode`, prefix-seek flag, min/max miss guards, read flags for flow statistics, and an optional missing-range cache. `seek` finds the first key greater than or equal to a target for forward/mixed scans; `seek_for_prev` finds the last key less than or equal to a target for backward/mixed scans. `near_seek` and `near_seek_for_prev` walk with `next` or `prev` while the cursor is near the target, falling back to full seek after `SEEK_BOUND`. `reverse_seek` and `near_reverse_seek` implement strict-less-than target positioning.

The missing-range cache is enabled only for mixed, non-prefix cursors. When a seek lands at an upper key greater than the target, `[target, upper)` can be cached as empty while the iterator remains at `upper`. Later seeks inside that range skip extra iterator movement. `key` and `value` update `CfStatistics` only once per cursor position. Iterator movement wraps stats collection by operation kind. `valid` converts iterator status errors into critical metrics, optional panic marks, or logged errors.

`CursorBuilder` converts optional lower/upper `Key` bounds into `KeyBuilder` bounds, configures `IterOptions` for fill-cache, prefix seek, timestamp hints, key-only reads, and max skippable internal keys, then creates a `Cursor`.

## State, Dependencies, and Integration
Cursor state is transient over a snapshot iterator. It integrates with `engine_traits::IterOptions`, TiKV key encoding, `CfStatistics`, RocksDB iterator metrics, failpoints, critical error metrics, and `Snapshot`. Prefix seek is restricted from `seek_to_first` and `seek_to_last`.

## Risks and Test Signals
Risks include stale missing-range caches, incorrect min/max miss shortcuts, prefix-seek end semantics, scan-mode misuse, and panics from invalid iterator assumptions. Tests cover prefix seek behavior, many missing-range cache hit/miss and invalidation cases with statistics assertions, and reverse iteration over region snapshots.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tikv_kv/src/cursor.rs -->
