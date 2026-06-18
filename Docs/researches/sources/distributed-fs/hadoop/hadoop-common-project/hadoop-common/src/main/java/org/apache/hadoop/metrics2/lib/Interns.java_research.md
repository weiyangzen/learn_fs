## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/lib/Interns.java

Purpose: Factory/cache for canonical `MetricsInfo` and `MetricsTag` value objects.

Important APIs/types/functions: `info(name,desc)` returns interned metadata; `tag(info,value)` and overloads return interned tags. Internal cache helpers bound cache sizes.

Control flow: Lookup-or-create paths reuse existing objects for repeated metadata/value combinations.

State and persistence: Static in-memory caches only; bounded to avoid unbounded growth.

Dependencies/integration: Used throughout registry, annotations, builders, system metrics, and tags.

Risks/test signals: Cache key equality and maximum size behavior are important. Tests should cover object reuse, different descriptions, different tag values, and cache eviction/bounds.
