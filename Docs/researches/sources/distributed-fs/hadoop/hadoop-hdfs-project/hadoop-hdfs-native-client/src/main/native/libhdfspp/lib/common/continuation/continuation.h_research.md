<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/continuation/continuation.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/continuation/continuation.h

## Purpose
Implements a small continuation-passing-style pipeline framework used to sequence asynchronous libhdfspp operations without deeply nested callbacks.

## Important APIs, Types, And Functions
`Continuation` defines `Run(const Next&)`. `Pipeline<State>` owns a state object, a vector of continuation stages, a current stage index, a user completion handler, and a `CancelHandle`. Key methods are `Create`, `Push`, `Run`, `state`, and private `Schedule`.

## Control Flow
Callers heap-create a pipeline, push stages, populate `state()`, and call `Run()`. `Schedule` checks cancellation, stops on non-OK status or end-of-stages, invokes the user handler, clears stages, and deletes the pipeline. Otherwise it runs the next stage with a bound callback back into `Schedule`.

## State And Persistence
Pipeline state and stages live only for one async operation and self-delete on completion. Cancellation is shared through `CancelTracker`; no durable state exists.

## Dependencies And Integration Points
Used by RPC and block reader flows with continuation stages from `asio.h`, `protobuf.h`, and protocol-specific code.

## Risks
Self-deletion requires every async path to call `next` at most once and never touch the pipeline afterward. A stage that never calls `next` leaks the pipeline and stalls the operation. Cancellation is only observed between stages.

## Test Signals
Tests should cover ordered stage execution, early error, cancellation before and during stages, handler state visibility, and double-callback or missing-callback defensive behavior in higher-level code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/continuation/continuation.h -->
