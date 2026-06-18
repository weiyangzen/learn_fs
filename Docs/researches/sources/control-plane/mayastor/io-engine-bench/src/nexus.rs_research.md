<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine-bench/src/nexus.rs -->
# sources/control-plane/mayastor/io-engine-bench/src/nexus.rs

Purpose: Criterion benchmark comparing direct in-process nexus creation against legacy gRPC nexus creation using a four-container compose cluster and an in-binary Mayastor environment.

Important APIs/types/functions: `build_type()` infers build profile from `OUT_DIR`/`SRCDIR`; `new_compose()` initializes composer and starts four io-engine containers; `new_environment()` creates `MayastorTest`; `get_children()` lazily creates and shares malloc bdevs over NVMf; `DirectNexus` and `GrpcNexus` destroy created nexuses in `Drop`; `nexus_create_direct()` calls `io_engine::bdev::nexus::nexus_create`; `nexus_create_grpc()` calls v0 gRPC `create_nexus`; `criterion_benchmark()` registers async Criterion cases.

Control flow: setup is done once per benchmark group. Child URIs are cached in a `tokio::sync::OnceCell`. Each iteration creates a unique nexus with three children and relies on large-drop cleanup to run destruction after measurement.

State and dependencies: depends on composer containers, gRPC v0 generated clients, Tokio runtime, UUIDs, NVMf ports, malloc bdev state, and global io-engine runtime state inside `MayastorTest`.

Risks and test signals: `Drop` creates fresh runtimes and unwraps destroy calls, so cleanup failures panic. Cached children assume the compose cluster remains valid for the full run. Benchmark timing includes API path and internal create work but not full cluster setup. Healthy output is two Criterion functions under `<build>/nexus/create`: `direct` and `grpc`.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine-bench/src/nexus.rs -->
