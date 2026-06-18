# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestQuotaUsage.java

Purpose: validates `QuotaUsage` builder defaults, quota accounting fields, formatted output, human-readable output, and equality.

Important APIs/types/functions: `QuotaUsage.Builder`, getters for file/directory count, namespace quota, space consumed/quota, `QuotaUsage.getHeader`, `toString`, `toString(true)`, `StorageType.SSD`, `typeConsumed`, `typeQuota`, and `equals`.

Control flow/state/persistence: pure DTO tests construct quota objects with no quota, namespace/space quota, and storage-type quota data; then assert getter values and exact formatted strings.

Dependencies/integration points: supports CLI/reporting consumers of quota output and storage-type quota accounting.

Risks/test signals: exact string assertions catch formatting regressions in user-facing quota reports, including `none`, `inf`, negative remaining quota, and human unit conversions.
