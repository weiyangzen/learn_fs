# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/qjournal/client/TestSegmentRecoveryComparator.java

Purpose: Unit test for `SegmentRecoveryComparator`, which ranks JournalNode `prepareRecovery` responses during QJM segment recovery.

Important APIs/types/functions: `SegmentRecoveryComparator.INSTANCE`, `PrepareRecoveryResponseProto`, `SegmentStateProto`, Mockito `AsyncLogger` placeholders, and logger-response map entries.

Control flow: The test builds in-progress responses with different end txids, an in-progress response with accepted epoch metadata, and a finalized response. It asserts equal self-comparison, longer in-progress winning over shorter in-progress, and finalized segments winning over longer or accepted in-progress segments.

State and persistence behavior: No durable state; recovery metadata is modeled with protobuf objects.

Dependencies and integration points: Comparator ordering feeds QJM recovery decisions before accept/finalize operations.

Risks: Bad ordering can select stale or unsafe segments, causing edit loss or invalid recovery.

Test signals: Passing confirms finalized logs outrank in-progress logs and length only decides among in-progress candidates.
