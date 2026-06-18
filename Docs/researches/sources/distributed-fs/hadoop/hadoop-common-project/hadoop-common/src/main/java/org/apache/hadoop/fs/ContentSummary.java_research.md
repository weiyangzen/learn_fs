## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/ContentSummary.java

Purpose: `ContentSummary` is a public, evolving summary object for file or directory content. It extends `QuotaUsage` and adds length, file count, directory count, snapshot-specific counters, snapshot space consumption, and erasure coding policy display support.

Important APIs and types: the nested `Builder` extends `QuotaUsage.Builder` and provides fluent setters for content, snapshot, quota, and storage-type quota fields. Public getters expose all summary fields. `write` and `readFields` implement legacy `Writable` serialization for length, file count, directory count, quota, space consumed, and space quota. Static header helpers and `toString` overloads produce CLI-style fixed-width summaries, quota summaries, storage-type quota summaries, erasure coding policy columns, and snapshot columns.

Control flow, state, and persistence: `Builder.build()` sets inherited file-and-directory count before constructing the object. Formatting chooses storage-type quota output when `tOption` is true, quota prefix when `qOption` is true, and optionally subtracts snapshot counts when `xOption` is true. Serialization intentionally omits snapshot fields and erasure coding policy, preserving older wire compatibility but losing newer state on a raw Writable round trip.

Dependencies and integration: this class is returned by filesystem content-summary operations and feeds command output such as quota and count reports. It depends on `QuotaUsage`, `StorageType`, `Writable`, and `StringUtils.TraditionalBinaryPrefix`.

Risks and test signals: `equals`, `hashCode`, and `toErasureCodingPolicy` dereference `erasureCodingPolicy`, so null policies can fail unless callers set a value. Tests should cover builder defaults, deprecated constructors, Writable compatibility, human-readable formatting, snapshot exclusion math, storage-type output, and null/replicated EC policy behavior.
