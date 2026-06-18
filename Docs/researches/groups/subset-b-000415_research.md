# subset-b-000415 research

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/host/resource.rs -->
# sources/control-plane/mayastor/io-engine/src/host/resource.rs

## Purpose
This file implements the host resource-usage query used by the gRPC host API. It is a small async wrapper around `getrusage(2)` for the current io-engine process.

## Important APIs, types, and functions
`Usage(pub libc::rusage)` is a transparent result wrapper so upper layers can serialize or map the raw libc structure. `get_resource_usage()` is the public async entry point and returns `RUSAGE_SELF`. The private `getrusage(who)` function owns the unsafe syscall boundary by allocating `MaybeUninit<libc::rusage>`, calling `libc::getrusage`, returning `Error::last_os_error()` on negative return, and `assume_init` only after success.

## Control flow
The call path is linear: public async method, syscall helper, raw `rusage` wrap. There is no reactor handoff or blocking work beyond the syscall itself.

## State and persistence behavior
No state is persisted or cached. The returned `rusage` is a point-in-time kernel snapshot of process CPU, memory, page fault, context switch, and I/O counters.

## Dependencies and integration points
The module depends on `libc` and standard `std::io::Error`. It integrates through `host` and gRPC code that exposes process diagnostics to the control plane.

## Risks and test signals
The unsafe block is narrow and guarded by the syscall return value. The code assumes the platform has libc `getrusage` and that `libc::rusage` layout matches the kernel ABI. Tests are likely integration-level host RPC tests; this file has no local unit tests.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/host/resource.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/jsonrpc.rs -->
# sources/control-plane/mayastor/io-engine/src/jsonrpc.rs

## Purpose
This module is the Rust adapter for SPDK JSON-RPC server methods. It lets handlers be written as serde-typed async Rust closures while SPDK calls a C ABI callback with raw JSON values and request pointers.

## Important APIs, types, and functions
`Code` maps project-level RPC errors to SPDK JSON-RPC integer codes, including standard JSON-RPC errors and negative errno-style codes for not found and already exists. `RpcErrorCode` is implemented by handler error types to choose an RPC code. `JsonRpcError` is the default error wrapper with `new`, `json_code`, `Display`, `Debug`, and `Error` implementations. `Result<T, E = JsonRpcError>` is the module alias.

`print_error_chain` flattens an error and all sources into one client-visible string. `extract_json_object` turns SPDK's `spdk_json_val` object pointer into the exact object substring by counting braces. `jsonrpc_register` boxes a Rust handler closure, converts the method name to `CString`, and registers `jsonrpc_handler` through `spdk_rpc_register_method`.

## Control flow
SPDK invokes `jsonrpc_handler` with a request, optional params, and the boxed handler pointer. The callback rebuilds the `Box<H>`, extracts or defaults params to `"null"`, deserializes to `P`, then schedules the user future on `Reactors::master()`. Handler success serializes `R` to JSON, writes the raw JSON value into SPDK's result writer, and ends the result. Handler failure logs the error chain and sends an SPDK error response with the handler's code. Parameter extraction/deserialization failures send invalid-params responses immediately.

## State and persistence behavior
Registered handler closures become leaked/runtime-owned pointers passed to SPDK. Requests are owned by SPDK; the module must finish or error them exactly once. No durable state is written.

## Dependencies and integration points
The module depends on `spdk_rs::libspdk` JSON-RPC functions, `serde`, `serde_json`, `futures`, `nix::errno`, and `Reactors`. It is used by server-side RPC modules that expose io-engine operations without hand-writing C JSON parsing.

## Risks and test signals
The callback reconstructs a `Box` from the raw handler pointer, which is risky if SPDK calls the method more than once because dropping the box would invalidate future invocations; review should confirm intended ownership or whether this should borrow instead. `extract_json_object` counts braces without string-literal awareness, so braces inside JSON strings can confuse it despite the comment that SPDK validates params. `CString::new(...).unwrap()` can panic if serialized output or error messages contain NUL bytes. Tests should cover multiple invocations of one registered method, object extraction with nested structures and strings, invalid params, and handler error mapping.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/jsonrpc.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/lib.rs -->
# sources/control-plane/mayastor/io-engine/src/lib.rs

## Purpose
This is the crate root for io-engine. It wires macro imports, declares the public module graph, re-exports SPDK FFI helpers, and provides C initialization hooks for SPDK subsystem/module registration.

## Important APIs, types, and functions
The file exposes major modules such as `core`, `bdev`, `grpc`, `host`, `jsonrpc`, `logger`, `lvm`, `lvs`, `pool_backend`, `replica_backend`, `rebuild`, `store`, `subsys`, and `target`. `pub use spdk_rs::ffihelper` makes SPDK callback helper utilities available through the crate.

`CPS_INIT!` exports a static function pointer in `.init_array` that points to `io_engine::cps_init`, allowing dependent binaries or modules to request early initialization. `cps_init()` registers the subsystem layer, nexus bdev module, and null-ng bdev module.

## Control flow
At library load or binary startup, users of `CPS_INIT!` arrange for `cps_init` to run before normal Rust main flow. That registration prepares SPDK-facing modules before runtime operations.

## State and persistence behavior
The file itself has no durable state, but `cps_init` mutates global SPDK/module registries. The module declarations define the crate's stable integration surface.

## Dependencies and integration points
It depends on macro crates (`ioctl_gen`, `tracing`, `serde`, `derive_builder`) and core external crates (`nix`, `serde_json`, `snafu`, `spdk_rs`). It is the integration root for all io-engine binaries and tests.

## Risks and test signals
Initialization order is the key risk: modules needing SPDK registration must be registered before use and must tolerate repeat or early calls. Tests are generally crate integration/build tests rather than local unit tests. Changes here have broad compile and startup impact.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/logger.rs -->
# sources/control-plane/mayastor/io-engine/src/logger.rs

## Purpose
This module configures io-engine logging and tracing. It bridges SPDK logs into Rust logging, provides default/compact/JSON formatters, supports optional hostname and eventing output, and exposes CLI-friendly span event options.

## Important APIs, types, and functions
`log_impl` is the C ABI callback used for SPDK logs; it maps `spdk_log_level` to `log::Level`, checks SPDK print level, converts C strings, and emits a Rust `log::Record` with target `mayastor::spdk`. `LogFormat` stores formatter options: ANSI, `LogStyle`, date, and hostname. `FromStr` parses comma-separated options such as `compact`, `json`, `color`, `nodate`, and `host`.

`FormatLevel`, `CustomContext`, `Location`, and `LogHostname` implement display helpers. `StringVisitor` extracts tracing event fields for JSON mode. `FmtSpan` maps CLI enum values to tracing subscriber span lifecycle flags. `init_ex` installs `LogTracer`, builds the tracing formatter layer, applies a rust-log filter, optionally adds an event publisher layer for `EVENTING_TARGET`, and installs the global subscriber. `init` is the default simple initializer.

## Control flow
Runtime setup flows through `init_ex`: initialize log-to-tracing bridge, create format/event layer filtered away from eventing target, build target/env filter, optionally initialize event publishing via `EventHandle::init_ext`, combine layers on `Registry`, and set the global default subscriber. Formatting branches per event into default, compact, or JSON style. SPDK logs enter through `log_impl`, then re-enter the same global logging pipeline.

## State and persistence behavior
The global tracing subscriber and `LogTracer` are process-global one-time state. `HOSTNAME_PREFIX` caches hostname in `OnceCell`. Logging does not persist directly except through configured stdout/stderr and event-publisher sinks.

## Dependencies and integration points
Dependencies include `tracing`, `tracing_subscriber`, `tracing_log`, `tracing_filter`, `ansi_term`, `chrono`, `event_publisher`, `once_cell`, `nix`, and SPDK log FFI. It integrates with CLI logging configuration, SPDK log callback registration, and control-plane event emission.

## Risks and test signals
`set_global_default` and `LogTracer::init` panic on repeated initialization, so tests or embedding processes must initialize once. `log_impl` dereferences raw C strings and unwraps file conversion. JSON style collapses recorded fields into a single `message` field and may not preserve structured tracing fields. Eventing filter correctness matters to avoid recursive event logs. Useful tests cover `LogFormat::from_str`, formatting modes, hostname toggling, and repeated-init behavior; this file has no local tests visible.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/logger.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/lvm/cli.rs -->
# sources/control-plane/mayastor/io-engine/src/lvm/cli.rs

## Purpose
This file is the async process-execution layer for the LVM backend. It wraps `pvcreate`, `vgcreate`, `lvs`, `dmsetup`, `blockdev`, and related commands, standardizes JSON report parsing, and provides query argument and serde helpers.

## Important APIs, types, and functions
`CmnQueryArgs` carries optional name, uuid, and tag filters with constructors for all resources, Mayastor-owned resources, and optional filters. `LvmSubCmd` maps enum variants to concrete command names using `strum`. `LvmCmd` wraps a `tokio::process::Command`, optional stdin, and command name.

Builder methods construct specific subcommands and append arguments/tags. `report<T>` expects LVM's top-level JSON `report` array and returns the first report block. `output_json<T>` decodes command stdout as JSON. `run` discards output on success. `output` executes the command, handles SPDK-thread trampoline via `crate::tokio_run!`, maps spawn failures and non-zero exits to `Error`, and logs the command at trace level. `cmder` optionally writes stdin and uses `pre_exec` to set `CLOEXEC` on fd range 3..1024. `de::number_from_string` and `de::comma_separated` decode LVM JSON fields.

## Control flow
Callers build a command fluently, then await `run`, `output`, `output_json`, or `report`. If running on an SPDK thread, process execution is submitted onto the tokio runtime and the result is returned through a oneshot bridge. JSON report callers depend on upstream arguments including `--report-format=json`.

## State and persistence behavior
The file itself keeps no durable state, but commands mutate host LVM/device-mapper state. LVM tags are passed as command-line flags through `Property::add`/`del`. Stdin is consumed once when present.

## Dependencies and integration points
It depends on `tokio::process`, `tokio::io::AsyncWriteExt`, `serde`, `snafu`, `nix`, `strum`, and the LVM property/error modules. It is the foundation used by `vg_pool`, `lv_replica`, and `dm_setup`.

## Risks and test signals
Command error mapping relies on stderr text at higher layers, so LVM version/localization changes are risky. `close_range(3,1024)` is a bounded best-effort fd cleanup and may miss higher descriptors. The SPDK-thread trampoline is critical to avoid blocking reactors. Tests should mock or isolate LVM binaries; high-value cases include JSON parse failures, report-missing, stdin command execution, non-zero exit mapping, and query argument validation.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/lvm/cli.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/lvm/dm_setup.rs -->
# sources/control-plane/mayastor/io-engine/src/lvm/dm_setup.rs

## Purpose
This module wraps `dmsetup` operations used by the LVM replica backend for suspending, resuming, inspecting, loading, and removing device-mapper devices.

## Important APIs, types, and functions
`DmState` represents `Suspended`, `Active`, `ReadOnly`, or an unknown string from `dmsetup info`. It implements `From<String>` and `Display`. `DmTable(pub String)` wraps a raw device-mapper table and implements `Display`. `DmSetup` provides async static methods: `suspend`, `resume`, `table`, `load`, `remove`, and `state`.

## Control flow
Each method builds an `LvmCmd::dm_setup()` command. `table` reads stdout, trims the trailing newline, and returns `DmTable`. `load` passes the table through stdin. `state` invokes `dmsetup info -C -osuspended --noheadings` and maps the trimmed result to `DmState`.

## State and persistence behavior
The wrapper changes kernel device-mapper state. `suspend` and `resume` affect I/O scheduling; `load` replaces the inactive/loaded table; `remove` removes a dm device. The file stores no Rust state.

## Dependencies and integration points
It depends on the LVM command wrapper and `super::Error`. `lv_replica` uses it for fault-injection-like `bork`/`unbork`, resize/device table management, and stale `/dev/<vg>` cleanup.

## Risks and test signals
These commands operate on live block devices, so tests need isolation. `suspend` may return before the device is fully suspended if open counts remain. `load` correctness depends on trusted table strings. `state` assumes the selected `dmsetup` field produces values matching the enum. Tests should cover state parsing and command invocation through a fake `dmsetup`.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/lvm/dm_setup.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/lvm/error.rs -->
# sources/control-plane/mayastor/io-engine/src/lvm/error.rs

## Purpose
This file defines the LVM backend error taxonomy and maps errors to errno values used by higher io-engine APIs.

## Important APIs, types, and functions
`Error` is a `snafu` enum covering command/report failures, VG/LV lookup and validation errors, unsupported features, reactor bridge failures, SPDK bdev import/export/share failures, metadata/tag update failures, and operation-specific states like `NoSpace`, `Exists`, `SnapshotNotSup`, and `GrowNotSup`. `fail<T>` supports `snafu::ensure!` style returns. `impl ToErrno` maps each variant to a stable `nix::errno::Errno`.

## Control flow
Errors are created by LVM command wrappers, pool/replica logic, and bdev integration paths. Conversion into pool/backend errors happens in `lvm/mod.rs` through `Into` implementations outside this file.

## State and persistence behavior
No runtime state is stored. The persistent behavioral contract is the user-facing display text and errno mapping.

## Dependencies and integration points
It depends on `snafu`, `nix`, `crate::core::ToErrno`, `crate::bdev_api::BdevError`, and `crate::core::CoreError`. It integrates with gRPC and backend error conversion paths that turn storage failures into API status/error codes.

## Risks and test signals
Errno mapping directly affects API behavior; changing it can break control-plane retries or user-visible semantics. Some command failures are mapped broadly to `EIO`, while higher layers recover specific cases by matching stderr strings. Tests should assert mappings for not found, exists, no space, unsupported features, and bdev errors.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/lvm/error.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/lvm/lv_replica.rs -->
# sources/control-plane/mayastor/io-engine/src/lvm/lv_replica.rs

## Purpose
This file implements LVM logical volumes as io-engine replicas. It lists and creates LVs through the LVM CLI, imports owned LVs as SPDK AIO bdevs, persists share metadata in LVM tags, supports NVMf share/unshare/update operations, and implements core replica/logical-volume traits.

## Important APIs, types, and functions
`QueryArgs` combines VG and LV filters and can query either regular LVM fields or Mayastor's tag-based LV identity. `LogicalVolume` is deserialized from `lvs` JSON and stores LV/VG identity, size, path, tags, and runtime state. `RunLogicalVolume` mirrors runtime share/name/entity/bdev state derived from tags and SPDK. `BdevOpts` snapshots SPDK bdev URI, share URI, allowed hosts, protocol, and size.

Key methods include `create`, `lookup`, `list`, `fetch`, `import`, `import_bdev`, `export_bdev`, `destroy`, `resize`, `share_nvmf`, `update_share_props`, `unshare`, `set_property`, `dm_suspend`, `dm_resume`, `table`, `bork`, and `unbork`. `LvolPtpl` implements `PtplFileOps` for per-replica NVMf persistence files under the parent VG PTPL path. Trait implementations expose the object through `crate::core::LogicalVolume` and `Share`.

## Control flow
Creation delegates to `VolumeGroup::create_lvoli`, then looks up the LV and treats an existing compatible LV as an import. Listing fetches LVM JSON, imports attributes from tags, then imports every owned LV as an SPDK AIO bdev. `import_bdev` constructs `aio://<lv_path>?uuid=<lv_uuid>`, creates the bdev if missing, applies persisted share/allowed-host state, then stores `BdevOpts`.

Share operations run SPDK work via `spdk_run!`, update the SPDK bdev, then synchronize LVM tags. Unshare can optionally persist `Protocol::Off`. Resize first resizes the LV, then notifies the SPDK bdev block count change and rolls back the LV size if bdev notification fails. Destroy exports/unshares/destroys the bdev before `lvremove` and PTPL cleanup.

## State and persistence behavior
Persistent state lives in LVM tags: Mayastor ownership, replica display name, share protocol, allowed hosts, and entity id. Runtime state mirrors those tags and SPDK bdev state. PTPL files are created for NVMf share persistence and removed on destroy. `tags_dirty` records failed tag updates but there is no visible repair loop in this file.

## Dependencies and integration points
The file depends on LVM command/query/property modules, `VolumeGroup`, `DmSetup`, SPDK bdev APIs, core `Share`/`LogicalVolume`/`UntypedBdev` traits, and pool backend types. It is surfaced through `lvm/mod.rs` factories and replica operations.

## Risks and test signals
The backend relies on LVM stderr strings for `NoSpace` and `Exists` mapping. Tag synchronization can fail after SPDK state changes, leaving runtime and persistent state divergent. `share_nvmf` contains a TODO noting wrong share URI behavior. `list` fails the whole list if any owned LV import fails. Resize rollback is best-effort. Tests should cover idempotent create/import, tag persistence and dirty failure, share/unshare persistence, allowed-host updates, resize rollback, export/destroy ordering, and dmsetup table fault paths.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/lvm/lv_replica.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/lvm/mod.rs -->
# sources/control-plane/mayastor/io-engine/src/lvm/mod.rs

## Purpose
This module is the public integration layer for the LVM backend. It documents LVM concepts, wires internal modules, exports pool/replica types, provides reactor bridging helpers, and implements io-engine pool and replica backend traits for LVM.

## Important APIs, types, and functions
The module re-exports `VolumeGroup`, `LogicalVolume`, `QueryArgs`, `CmnQueryArgs`, and `Error`. `is_alphanumeric` validates query values allowed in LVM `--select` expressions. `tokio_submit`, `spdk_run!`, and `tokio_run!` bridge work between SPDK reactor context and tokio process execution.

Trait implementations include `PoolOps` and `IPoolProps` for `VolumeGroup`, `ReplicaOps`, `SnapshotOps`, and `BdevStater` for `LogicalVolume`, plus `PoolLvmFactory` and `ReplLvmFactory` implementing backend factory interfaces.

## Control flow
Pool create/import/list/find calls route to `VolumeGroup` methods when the LVM feature is enabled. Replica list/find routes to `LogicalVolume::lookup/list` with Mayastor tag filters. Replica operations delegate share/unshare/update/resize/destroy to `lv_replica`. Snapshot and clone methods return unsupported or empty lists because LVM snapshots are not implemented for this backend.

## State and persistence behavior
This file does not persist directly, but it decides which persistent LVM-tagged pools and replicas are visible to the generic backend layer. Factory methods filter by feature flags and requested `PoolBackend`. Stats and grow/reset are currently unsupported for LVM.

## Dependencies and integration points
It depends on core logical-volume/share/stats traits, pool and replica backend traits, LVM property types, and futures oneshot channels. It is the main adapter consumed by control-plane APIs that operate generically over pool backends.

## Risks and test signals
Feature-gate checks must stay consistent across find/list paths; `ReplLvmFactory::find` does not check the LVM feature flag while list does. Snapshot methods intentionally return unsupported/empty behavior, which callers must handle. `FindPoolArgs::UuidOrName` currently treats the value as uuid only. Tests should exercise backend filtering, feature disabled behavior, pool/replica trait conversions, unsupported operations, and reactor tokio bridge errors.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/lvm/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/lvm/property.rs -->
# sources/control-plane/mayastor/io-engine/src/lvm/property.rs

## Purpose
This file defines LVM tags used as persistent metadata for Mayastor-owned LVM volume groups and logical volumes.

## Important APIs, types, and functions
`impl_properties!` generates the `Property` enum, `PropertyType` enum, typed value accessors, key lookup, and `FromStr` parsing. The configured properties are ownership tag `Lvm` with key `mayastor`, `LvName`, `LvShare`, `LvAllowedHosts`, and `LvEntityId`. `Property::value`, `tag`, `add`, and `del` render tags and LVM command flags. `Property::new` parses raw LVM tag strings into known or `Unknown(key,value)` values. `Protocol::value_str` and `from_value` map `Off`/`Nvmf` to persisted strings.

## Control flow
LVM JSON deserialization uses `FromStr` to turn comma-separated tag strings into `Property` values. Command builders call `add`/`del` to mutate tags. Runtime import code extracts typed values with generated accessors.

## State and persistence behavior
These properties are persisted in LVM metadata, so they survive process restarts and host reboots. Unknown tags are preserved as values when parsed, but update code for a known type may delete old properties of that type before adding the new one.

## Dependencies and integration points
It depends on `crate::core::Protocol` and standard `FromStr`. `vg_pool` uses the ownership tag, while `lv_replica` uses name/share/allowed-host/entity tags for replica import and share restoration.

## Risks and test signals
`Property::new` splits on `=` and only accepts exactly zero or one separator; values containing `=` become `Unknown` for the full tag. `Protocol::from_value` defaults unknown values to `Off`, which can hide corrupted share metadata. Tag values must remain compatible with LVM tag character rules and `is_alphanumeric` query validation. Tests should cover parsing, rendering add/delete flags, unknown tags, allowed-host lists, and protocol fallback.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/lvm/property.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/lvm/vg_pool.rs -->
# sources/control-plane/mayastor/io-engine/src/lvm/vg_pool.rs

## Purpose
This file implements LVM volume groups as io-engine pools. It creates/imports VGs, lists and filters VG metadata, creates logical-volume replicas, exports/destroys pools, and manages VG-level PTPL directory cleanup.

## Important APIs, types, and functions
`QueryArgs` wraps common query arguments and renders VG-specific `--select` expressions for name, uuid, and tags. `VolumeGroup` deserializes `vgs` JSON fields: name, uuid, size, free, tags, and physical disks. Important methods include `lookup`, `list`, `create`, `import`, `import_inner`, `create_lvol`, `list_lvs`, `list_foreign_lvs`, `destroy`, `purge`, `destroy_`, `export`, `export_all`, and `create_lvoli`. `VgPtpl` implements pool PTPL subpath handling under `pool/vg/<name>`.

## Control flow
Create first checks whether a VG with the requested name exists. Existing VGs go through import validation. Missing VGs run `pvcreate` on disks, then `vgcreate` with optional Mayastor tag, with special stale `/dev/<name>` dm cleanup on a known error. Import validates that users did not provide a VG uuid, verifies disk list equality, and adds or removes the Mayastor ownership tag depending on `no_spdk`. Destroy exports owned LVs first, then removes VG/PVs unless foreign LVs remain or purge is requested.

`create_lvoli` rejects thin provisioning, creates an LV using the replica uuid as LV name, adds metadata tags, maps known stderr text to `NoSpace`/`Exists`, and logs success.

## State and persistence behavior
Persistent state is host LVM metadata: PV labels, VG metadata, ownership tags, and LV tags. Export removes Mayastor tags and unloads bdevs but leaves VG/LV data. Destroy removes VG/PV metadata and PTPL directories if safe.

## Dependencies and integration points
It depends on `LvmCmd`, deserializer helpers, `Property`, `DmSetup`, `LogicalVolume`, `PoolArgs`, and `PtplFileOps`. `lvm/mod.rs` exposes it as `PoolOps`/`IPoolProps`.

## Risks and test signals
Disk comparison is order-sensitive, which may reject semantically identical VG disk sets. Create/import behavior changes with `no_spdk`, so ownership tags can be removed intentionally. Destroy leaves pools with foreign LVs, which is safe but can surprise callers. Stderr-prefix matching is brittle. Tests should cover create/import/no_spdk flows, disk mismatch, foreign LV retention, purge, stale dm cleanup, LV creation error mapping, and query validation.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/lvm/vg_pool.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/lvs/lvol_iter.rs -->
# sources/control-plane/mayastor/io-engine/src/lvs/lvol_iter.rs

## Purpose
This file provides iterators over SPDK lvols globally and within one LVS pool.

## Important APIs, types, and functions
`LvolIter(BdevIter<()>)` scans all bdevs and returns only those convertible to `Lvol`. `LvsLvolIter` walks the raw SPDK tail queue of `spdk_lvol` objects for a specific `Lvs`.

## Control flow
`LvolIter::next` loops over `BdevIter` until `Lvol::ok_from` succeeds or iteration ends. `LvsLvolIter::new` stores the first `tqh_first` pointer from the store. Its `next` returns the current lvol and advances to `link.tqe_next`.

## State and persistence behavior
The iterators hold raw or wrapper iteration state only. They do not persist. `LvsLvolIter` is explicitly safe only while the underlying list is not modified.

## Dependencies and integration points
It depends on `crate::core::BdevIter`, `super::Lvol`, and SPDK lvol tail queue layout. `Lvs::lvols()` uses `LvsLvolIter`; global clone/snapshot listing often scans through bdevs.

## Risks and test signals
Raw pointer iteration can become invalid if async work or reactor activity mutates the lvol list during iteration. The comments warn callers not to run async code while holding the iterator. Tests should cover filtering non-lvol bdevs and pool-local iteration under stable lists; concurrency hazards require integration discipline.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/lvs/lvol_iter.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/lvs/lvol_snapshot.rs -->
# sources/control-plane/mayastor/io-engine/src/lvs/lvol_snapshot.rs

## Purpose
This file implements snapshot and clone operations for SPDK lvol replicas. It prepares blob xattrs, calls SPDK snapshot/clone APIs, lists snapshot descriptors, handles discarded snapshots, and calculates snapshot usage for clone chains.

## Important APIs, types, and functions
`LvolSnapshotOps` defines the common local/remote snapshot interface. It includes create/destroy/list/clone methods plus lower-level xattr preparation and SPDK callback helpers. `LvolResult` aliases `Result<*mut spdk_lvol, Errno>`. `LvolSnapshotDescriptor` pairs a snapshot `Lvol` with `SnapshotInfo` and converts into `SnapshotDescriptor`. `LvolSnapshotIter` follows parent blobs to enumerate snapshot ancestors.

The `impl LvolSnapshotOps for Lvol` implements `prepare_snapshot_xattrs`, `create_snapshot_inner`, `do_create_snapshot`, `prepare_clone_xattrs`, `create_clone_inner`, `do_create_clone`, descriptor builders, `create_snapshot`, `destroy_snapshot`, list methods, `create_clone`, clone listing, pending discarded snapshot cleanup, and clone-source snapshot usage calculation.

## Control flow
Snapshot creation validates required `SnapshotParams`, builds SPDK xattr descriptors backed by live `CString` storage, calls `vbdev_lvol_create_snapshot_ext`, waits on a oneshot callback, emits an event, and returns `Lvol`. Clone creation mirrors that flow with clone xattrs and `vbdev_lvol_create_clone_ext`. Destroy either destroys immediately when no clones exist or marks `DiscardedSnapshot=true` in metadata. Import cleanup later destroys discarded snapshots with no clones. Listing scans lvol bdevs, filters snapshots/clones by xattrs, and builds descriptors.

## State and persistence behavior
Snapshot and clone identity is persisted in SPDK blob xattrs: transaction id, entity id, parent id, snapshot uuid, creation time, discarded marker, source uuid, clone uuid, and clone creation time. Destroy may leave a discarded snapshot until dependent clones are removed.

## Dependencies and integration points
It depends on SPDK lvol snapshot/clone APIs, `SnapshotParams`, `CloneParams`, `SnapshotXattrs`, `CloneXattrs`, eventing, `LvsLvol`, and `UntypedBdev` iteration. `Lvs::import_from_args_` calls pending discarded snapshot cleanup after pool import.

## Risks and test signals
Required parameter validation is manual; missing values return configuration errors. Raw xattr descriptor pointers rely on local `CString` lifetimes until SPDK call submission. Global `Lvol::lookup_by_uuid_str` is used in parent iteration with a TODO to search only the owning store. Listing all snapshots scans all bdevs, which can be expensive and cross-pool if filters fail. Tests should cover xattr validation, create/clone callback errno mapping, descriptor validity with missing xattrs, discarded snapshot lifecycle, clone list accuracy, and usage accounting in clone chains.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/lvs/lvol_snapshot.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/lvs/lvs_bdev.rs -->
# sources/control-plane/mayastor/io-engine/src/lvs/lvs_bdev.rs

## Purpose
This file wraps SPDK's `lvol_store_bdev` structure, which links an lvol store to its backing bdev.

## Important APIs, types, and functions
`LvsBdev` stores `NonNull<lvol_store_bdev>`. `from_inner_ptr` constructs it from an SPDK pointer. `lvs` returns the `Lvs` store. `lvs_opt` hides stores whose base bdev is no longer present. `name` returns the pool name. `base_bdev` wraps the backing SPDK bdev pointer as `UntypedBdev`. `iter` returns an `LvsBdevIter`.

## Control flow
The wrapper is synchronous and pointer-based: read SPDK struct fields, convert inner pointers into Rust wrappers, and optionally filter invalid/removing stores through `base_bdev_opt`.

## State and persistence behavior
No persistence is performed. The struct is a borrowed view of live SPDK global state and is only valid while SPDK keeps the underlying object alive.

## Dependencies and integration points
It depends on `spdk_rs::libspdk::lvol_store_bdev`, `crate::core::{Bdev, UntypedBdev}`, and LVS iterator/store wrappers. `LvsIter` uses it to enumerate pools.

## Risks and test signals
The file documents the core risk: holding this wrapper across async/reactor progress can leave dangling pointers if the pool is destroyed. `base_bdev` unwraps pointer conversion and will panic on invalid SPDK state. Tests should exercise iteration and filtering of removing stores in controlled SPDK integration tests.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/lvs/lvs_bdev.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/lvs/lvs_error.rs -->
# sources/control-plane/mayastor/io-engine/src/lvs/lvs_error.rs

## Purpose
This file defines the error model for the SPDK logical volume store backend and maps SPDK/blobstore/core failures to errno values.

## Important APIs, types, and functions
`ImportErrorReason` adds import context such as not found/corrupt metadata, I/O inspection failure, name mismatch, name clash, and uuid mismatch. `BsError` normalizes low-level blobstore errno values into named errors such as invalid argument, lvol not found, already exists, busy, cannot import, no space, out of metadata, capacity overflow, crypto vbdev failure, and LVS removing. It provides `from_errno`, `from_i32`, and `ToErrno`.

`LvsError` covers pool import/create/export/destroy/grow, invalid bdev/input, replica create/destroy/resize, share/unshare/property errors, snapshot/clone errors, wipe failures, resource locking, metadata expansion parse errors, bdev rescan/grow failures, and crypto resize lag. `impl ToErrno` maps all high-level variants to API errno semantics.

## Control flow
SPDK callbacks and FFI return codes are converted into `BsError`, then wrapped into operation-specific `LvsError` variants at call sites. Higher layers use `ToErrno` for gRPC/API error mapping.

## State and persistence behavior
The file stores no mutable state. Its display strings and errno mappings are persistent API behavior. Import reason text is appended to import errors for diagnostics.

## Dependencies and integration points
It depends on `snafu`, `nix::errno`, `BdevError`, `CoreError`, `ToErrno`, and `PropName`. It is used throughout `lvs_store`, `lvs_lvol`, and `lvol_snapshot`.

## Risks and test signals
Correct errno mapping is critical for control-plane retry and idempotency behavior. `BsError::from_i32` accepts both positive and negative values and warns for negative input, reducing but not eliminating callback convention mistakes. Import with `InvalidArgument` is remapped by reason, so adding reasons requires mapping updates. Tests should cover every important errno conversion, especially import reasons, no space, exists, busy, unsupported grow, and crypto resize failures.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/lvs/lvs_error.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/lvs/lvs_iter.rs -->
# sources/control-plane/mayastor/io-engine/src/lvs/lvs_iter.rs

## Purpose
This file provides iterators over SPDK lvol stores by walking SPDK's global lvol-store-bdev list.

## Important APIs, types, and functions
`LvsBdevIter` holds the current `lvol_store_bdev` pointer and a `list_removing` flag. `LvsIter` wraps `LvsBdevIter` and yields `Lvs` stores rather than the backing bdev wrapper.

## Control flow
`LvsBdevIter::new` starts at `vbdev_lvol_store_first`. Each `next` returns the current wrapper and advances through `vbdev_lvol_store_next`. `LvsIter::next` either yields every store, including removing ones, or filters through `lvs_opt` so stores without base bdevs are hidden.

## State and persistence behavior
The iterator stores only live raw pointer cursor state. It does not persist data and must be treated as a synchronous view over SPDK global state.

## Dependencies and integration points
It depends on SPDK FFI list functions and `LvsBdev`. `Lvs::iter` and `Lvs::iter_all` expose these iterators to pool listing/export flows.

## Risks and test signals
The raw pointer cursor can become invalid if the SPDK list changes during iteration. Filtering behavior is important for export/removal paths: normal iteration hides removing pools, while `iter_all` includes them. Integration tests should cover both modes and pool cleanup during removal.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/lvs/lvs_iter.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/lvs/lvs_lvol.rs -->
# sources/control-plane/mayastor/io-engine/src/lvs/lvs_lvol.rs

## Purpose
This file implements SPDK lvol replicas as io-engine logical volumes. It wraps `spdk_lvol`, exposes share and logical-volume traits, manages blob xattr properties, handles resize/destroy/wipe operations, and computes space usage including snapshots and clones.

## Important APIs, types, and functions
`PropValue` and `PropName` represent persisted lvol metadata for shared state, allowed hosts, and entity id. `Lvol` wraps `NonNull<spdk_lvol>` and can be constructed from an `UntypedBdev` when the bdev driver is `lvol`. `WIPE_SUPER_LEN` defines the 8 MiB fallback zeroing length when unmap is unavailable. `ResizeCbCtx` bridges resize callback state.

Important methods include `lookup_by_uuid_str`, `wipe_super`, `lvol_cb`, `ptpl`, `blob_xattr`/`get_blob_xattr`, `set_blob_attr`, clone-count helpers, and `lvol_resize_cb`. `LvolPtpl` manages per-replica PTPL files. `LvsLvol` is the lvol-specific trait extending `LogicalVolume + Share` with store/bdev access, metadata get/set/sync, blob iteration, destroy, and resize.

## Control flow
Share implementation delegates to the underlying bdev's NVMf share, then persists `Shared(true)` and allowed hosts into blob xattrs. Unshare delegates to bdev unshare and optionally persists `Shared(false)`. Property updates can set allowed hosts without metadata sync before updating the live bdev.

Destroy unshares without persisting, calls `vbdev_lvol_destroy`, removes PTPL, emits a delete event, and returns the name. `destroy_replica` also destroys a discarded source snapshot when the last clone disappears. Resize calls `vbdev_lvol_resize`, verifies callback success and resulting size, and maps errno. Metadata setters compare existing xattr values, set new xattrs, and sync blob metadata only when changed.

## State and persistence behavior
Persistent state lives in SPDK blob xattrs and PTPL JSON files. Runtime state is derived from live SPDK bdev/lvol structures. Snapshot/clone state is interpreted from xattrs defined in core. Wipe behavior writes zeros to the beginning of the lvol when unmap clearing is not available.

## Dependencies and integration points
It depends on SPDK blob/lvol APIs, core `LogicalVolume`, `Share`, bdev traits, snapshot/clone xattrs, eventing, `Lvs`, `LvsError`, and PTPL helpers. `lvs_store` creates `Lvol`s and `lvol_snapshot` extends them.

## Risks and test signals
The wrapper is pointer-heavy and must run on the correct SPDK reactor lifetime. Property setters ignore writes on snapshots and warn on read-only blobs. `share_uri` appends the lvol uuid as a query parameter, so callers must not double-append. `set_no_sync` compares sorted allowed hosts to avoid unnecessary metadata sync. Tests should cover property get/set/sync, share/unshare persistence, PTPL creation/destruction, wipe fallback, resize callback failure, clone-count behavior, and logical-volume usage accounting.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/lvs/lvs_lvol.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/lvs/lvs_store.rs -->
# sources/control-plane/mayastor/io-engine/src/lvs/lvs_store.rs

## Purpose
This file implements SPDK logical volume stores as io-engine pools. It creates/imports/destroys/exports/grows blobstores on backing bdevs, manages optional crypto wrapping, auto-restores shared lvols, tracks pool I/O stall state, and creates replicas.

## Important APIs, types, and functions
`Lvs` wraps `NonNull<spdk_lvol_store>` and exposes lookup, iteration, capacity/free/used/committed, base-bdev access, metadata page stats, uuid, encryption detection, stall detection, import/create/export/destroy/grow, snapshot/lvol iteration, and lvol creation. `LvsBackendBdevs` owns the bdev setup/rollback context for pool create/import, including base bdev ops, crypto bdev state, and top-level pool bdev name. Constants define 1 MiB cluster alignment, 4 MiB default cluster size, and 1 GiB maximum cluster size. `LvsPtpl` manages pool-level PTPL directories under `pool/<uuid>`.

## Control flow
Create/import starts by parsing a single disk URI, creating the underlying bdev if missing, optionally creating a crypto vbdev, and replacing pool args with the top-level bdev name. Import rejects claimed bdevs, calls `vbdev_lvs_import`, validates pool name and optional uuid, restores shared replicas, creates pool info cache, enables stall detection, and destroys pending discarded snapshots. Create validates cluster size and metadata expansion ratio, calls SPDK lvs create with or without explicit uuid, then looks up the created pool and enables tracking.

Export and destroy unshare all lvol bdevs without persisting unshare state, unload or destruct the SPDK store, remove pool info if gone, clean up crypto/base bdevs, and remove PTPL on destroy. Grow rescans AIO/uring base bdevs, waits for crypto bdev resize if encrypted, updates blobstore block count, calls live grow, and verifies capacity increased. `share_all` reads persisted `Shared`/`AllowedHosts` xattrs and retries briefly while old unshare operations complete.

## State and persistence behavior
Persistent pool state lives on the backing blobstore superblock and blob metadata. Persistent share state for replicas lives in lvol xattrs and PTPL files. In-memory pool status is stored in `pool_information` cache, including I/O stalled state and transition timestamps. Create/import rollback destroys bdevs created during the failed attempt.

## Dependencies and integration points
The file depends on SPDK lvs/blobstore APIs, bdev URI/create/destroy APIs, crypto vbdev helpers, core bdev/share/reactor/environment types, eventing, `Lvol`, snapshot cleanup, pool args, pool info cache, and mayastor sleep. It is the core implementation used by the LVS backend factories outside this subset.

## Risks and test signals
Pool creation assumes exactly one disk. Import can hang if a bdev is examined while already claimed, so it checks `is_claimed` first. `share_all` has a fixed two-second retry window and logs but does not fail import on share restoration failure. Grow support depends on AIO/uring rescan and async crypto resize events. Stall handling disables timeout callbacks during reset and relies on superblock read to mark recovery. Tests should cover import/create rollback, encrypted pool setup/cleanup, uuid/name mismatch errors, cluster-size and max-expansion validation, auto-share restoration, destroy/export cleanup, live grow, and I/O stall reset transitions.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/lvs/lvs_store.rs -->
