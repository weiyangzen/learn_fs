# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/audit/CommonAuditContext.java

## Purpose
Thread-local and global context map for audit spans. It carries common key/value data such as process id, current thread id, command entry point, and user-supplied audit attributes.

## Important APIs, Types, and Functions
Public APIs include currentAuditContext(), put/remove/get/reset/containsKey(), getEvaluatedEntries(), global set/get/remove, getGlobalContextEntries(), currentThreadID(), and noteEntryPoint(Object).

## Control Flow
A static process UUID is installed globally under PARAM_PROCESS. ACTIVE_CONTEXT lazily creates one CommonAuditContext per thread and init() adds PARAM_THREAD1 as a dynamic supplier. put(String,String) stores constant suppliers; put(String,Supplier) stores dynamic suppliers. noteEntryPoint records the simple class name under PARAM_COMMAND if absent.

## State and Persistence Behavior
Global state is a ConcurrentHashMap shared by all threads. Per-thread context stores Supplier<String> values in a ConcurrentHashMap and may be retained by audit spans crossing thread boundaries. No durable persistence.

## Dependencies and Integration Points
Depends on AuditConstants, ThreadLocal, ConcurrentHashMap, UUID, and SLF4J. Used by filesystem audit spans and HTTP referrer audit header construction.

## Risks and Test Signals
Main risks are supplier memory retention, supplier thread-safety, global context overuse, and stale thread-local entries in pooled threads. Tests should cover reset, dynamic thread IDs, concurrent global iteration, noteEntryPoint idempotence, and supplier evaluation after span handoff.
