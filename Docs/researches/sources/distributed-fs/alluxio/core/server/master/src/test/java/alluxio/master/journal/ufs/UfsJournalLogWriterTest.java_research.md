# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/journal/ufs/UfsJournalLogWriterTest.java

Purpose: extensive tests for UFS journal log writer rotation, flush semantics, recovery after UFS failures, and detection of missing entries.

Important APIs/types/functions: uses `UfsJournalLogWriter`, `UfsJournalReader`, `UfsJournalSnapshot`, `UfsJournalFile`, `UnderFileSystem.supportsFlush`, `ExceptionMessage.JOURNAL_ENTRY_MISSING`, and PowerMock `Whitebox` to replace the writer's internal `DataOutputStream`.

Control flow: setup starts a primary UFS journal. Completion tests convert current incomplete logs into completed logs and deduplicate already completed logs. Write tests compare flush-supported UFS, which keeps one log until close, against non-flush UFS, which rotates on flush. Rotation test sets max log size to one byte and expects every entry to become its own log. Recovery tests inject write or flush failures, verify the writer resets its stream, retries writes/flushes, completes files after failed flush, and can recover after deleting an incomplete file. Missing-entry tests truncate or delete files after acknowledged flushes and expect runtime errors containing precise missing sequence ranges.

State and persistence behavior: exercises real local journal files, completed/incomplete log naming, and reader verification of sequence intervals. Failure injection mutates the active stream while files are partially written.

Dependencies and integration points: integrates with UFS flush capability, journal reader recovery scanning, log rotation configuration, runtime debug URL error messages, and snapshot current-log discovery.

Risks: relies on reflection into private writer internals. Local filesystem behavior may not represent all UFS backends. Sequence-only entries do not cover payload decode failures.

Test signals: very strong regression coverage for the most failure-prone UFS log writer paths, especially preserving or detecting flushed journal entries across I/O errors.
