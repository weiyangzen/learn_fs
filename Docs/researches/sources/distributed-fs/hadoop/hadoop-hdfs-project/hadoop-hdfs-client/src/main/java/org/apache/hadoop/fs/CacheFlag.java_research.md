# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/fs/CacheFlag.java

Purpose: public evolving enum for cache directive operation flags.

Important APIs and types: only enum value is `FORCE`, documented to ignore cache pool resource limits. Each flag holds a short mode, exposed package-locally through `getMode()`.

Control flow and state: no dynamic control flow beyond enum construction. Mode value `0x01` is used for protocol/operation encoding by neighboring cache directive code.

Dependencies and integration: annotated public/evolving and intended for `EnumSet<CacheFlag>` composition in cache APIs.

Risks and test signals: small surface, but mode stability matters for wire or server interpretation. `getMode()` is package-private, constraining external callers to enum constants rather than numeric values.
