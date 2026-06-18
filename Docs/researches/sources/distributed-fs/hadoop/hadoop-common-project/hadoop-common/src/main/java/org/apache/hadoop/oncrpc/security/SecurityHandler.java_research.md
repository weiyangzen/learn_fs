# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/security/SecurityHandler.java

Purpose: abstract per-request security adapter used by ONC RPC services to map credentials to users, decide drops, produce verifiers, and optionally wrap/unwrap GSS payloads.

Important APIs/types/functions: abstract `getUser`, `shouldSilentlyDrop`, `getVerifer`; defaults `isUnwrapRequired`, `isWrapRequired`, `unwrap`, `wrap`, `getUid`, `getGid`, and `getAuxGids`.

Control flow: base defaults indicate no wrapping and throw `UnsupportedOperationException` for GSS and AUTH_SYS-specific operations unless overridden.

State and persistence: no fields; subclasses provide state.

Dependencies and integration: used by NFS/ONC RPC service implementations. Depends on `RpcCall`, `Verifier`, and `XDR`.

Risks: method name `getVerifer` is misspelled and is part of the API. Callers must check `isWrapRequired`/`isUnwrapRequired` before invoking default throwing methods. AUTH_SYS getters throw unless subclass is `SysSecurityHandler`.

Test signals: subclass tests and service tests should verify user mapping, verifier creation, and drop/wrap decisions.
