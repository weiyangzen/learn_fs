# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/audit/TestCommonAuditContext.java

Purpose: verifies global and thread-local behavior of `CommonAuditContext`, including default process/thread entries, dynamic values, entry point notation, and add/remove operations.

Important APIs/types/functions: `CommonAuditContext.currentAuditContext`, `setGlobalContextEntry`, `getGlobalContextEntry`, `getGlobalContextEntries`, `removeGlobalContextEntry`, `noteEntryPoint`, constants `PARAM_COMMAND`, `PARAM_PROCESS`, `PARAM_THREAD1`, and `PROCESS_ID`.

Control flow/state/persistence: tests set a global command entry and enumerate globals, verify process ID global entry, assert process is not present in the current local context, compare thread ID value to current thread id, reset context and install a supplier-backed dynamic key that reflects `AtomicBoolean` changes, set command entry point from `this` and null, and add/remove a local key.

Dependencies/integration points: uses AssertJ, `AbstractHadoopTestBase`, Java streams, and atomic supplier state. It guards audit metadata consumed by filesystem audit logs.

Risks/test signals: catches loss of dynamic evaluation, global/local context confusion, missing default process/thread identifiers, stale command entry point state, and broken enumeration/removal semantics.
