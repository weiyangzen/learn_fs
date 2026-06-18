# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/CallerContext.java

## Purpose

`CallerContext` is an immutable auditing context attached to Hadoop RPC calls. It carries a context string and optional signature so servers can log coarse-grained caller information.

## Important APIs, control flow, and state

The immutable object stores `context` and a defensive-copy `signature`. `isContextValid()` requires a non-empty context. `toString()` renders `context` and, when present, `:` plus the UTF-8 signature. Equality includes both context and signature, while `hashCode()` only includes context through `HashCodeBuilder`.

The nested `Builder` appends raw fields, key/value fields, or key/value only if absent. It validates the field separator against tab, newline, and equals. The current context is held in an `InheritableThreadLocal` via holder idiom methods `getCurrent()` and `setCurrent()`.

## Dependencies and integration points

Caller context is serialized in RPC headers (`RPCCallerContextProto`) and reconstructed in `Server`. Constants define common audit field names such as client IP, port, client ID, call ID, real user, and proxy user port.

## Risks and test signals

The `appendIfAbsent()` check is substring-based on `key + ":"`, so keys embedded in values could produce false positives. Signature bytes are copied on set/get, but `Builder.getSignature()` returns the builder's internal array to the private constructor, relying on builder usage discipline. Thread-local inheritance can leak context into child threads if not cleared. `TestCallerContext` covers append behavior, append-if-absent behavior, and builder construction.
