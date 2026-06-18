# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/VersionUtil.java

Purpose: `VersionUtil` wraps Hadoop's Maven-compatible `ComparableVersion` for comparing version strings.

Important APIs/types/functions: `compareVersions(String, String)` constructs two `ComparableVersion` instances and returns `compareTo`.

Control flow: direct object construction and comparison with no extra validation.

State and persistence behavior: stateless.

Dependencies and integration points: depends on `ComparableVersion`, matching Maven version ordering semantics used by compatibility checks.

Risks: null or unusual version strings are handled according to `ComparableVersion`, not this wrapper. Callers must interpret negative/zero/positive return values correctly.

Test signals: tests should cover numeric versions, qualifiers such as snapshot/alpha, equality normalization, and null behavior if callers can pass nulls.
