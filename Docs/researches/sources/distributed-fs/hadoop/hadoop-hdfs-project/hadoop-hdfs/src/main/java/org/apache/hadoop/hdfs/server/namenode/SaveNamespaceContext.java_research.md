# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/SaveNamespaceContext.java

## Purpose
`SaveNamespaceContext` carries shared state for an active saveNamespace operation: source namesystem, target txid, storage-directory errors, cancellation, and completion.

## Important APIs, types, and functions
Fields are `FSNamesystem sourceNamesystem`, `txid`, synchronized `List<StorageDirectory> errorSDs`, `Canceler canceller`, and one-shot `CountDownLatch completionLatch`. Methods expose namesystem/txid, report and retrieve errored storage directories, mark completion, and check cancellation.

## Control flow
Save tasks call `checkCancelled()` at safe points; it throws `SaveNamespaceCancelledException` with the cancel reason. `reportErrorOnStorageDirectory` accumulates failed storage directories. `markComplete` asserts the context has not already completed and counts down the latch.

## State and persistence behavior
The context is transient per save. Its txid identifies the namespace image being saved. `errorSDs` records persistent storage directories that failed so higher layers can handle them. It does not write storage directly.

## Dependencies and integration points
It depends on `FSNamesystem`, `StorageDirectory`, `Canceler`, `CountDownLatch`, synchronized lists, `Preconditions`, and `SaveNamespaceCancelledException`. It is part of FSImage/saveNamespace coordination.

## Risks and invariants
Completion is single-use. The synchronized list still requires care during iteration. Cancellation must be checked often enough to avoid long uninterruptible saves. Cancellation and storage errors must remain distinct.

## Test signals
`TestSaveNamespace` should cover cancellation reason propagation, storage-directory error accumulation, double completion assertion, txid propagation, and consistent state after canceled saves.
