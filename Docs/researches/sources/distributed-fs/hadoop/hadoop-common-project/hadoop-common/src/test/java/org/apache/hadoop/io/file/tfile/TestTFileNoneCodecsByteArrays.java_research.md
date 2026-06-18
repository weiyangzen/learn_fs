
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/file/tfile/TestTFileNoneCodecsByteArrays.java

Purpose: Runs the byte-array TFile base suite with no compression and memcmp ordering.

Important APIs and types: Extends `TestTFileByteArrays` and configures `Compression.Algorithm.NONE.getName()`, `memcmp`, and expected records per block of 24 and 24.

Control flow: `setUp()` initializes the inherited compression/comparator/block-count settings and delegates to base setup. All behavior comes from `TestTFileByteArrays`, including sorted scans, seeks, block index checks, metadata, negative input cases, and compression effectiveness checks adjusted for none compression.

State and persistence: Uses inherited local temp file lifecycle and writer/reader state.

Dependencies and integration points: Provides baseline TFile behavior without codec effects, useful for isolating format and scanner logic.

Risks: Small expected block counts are tied to the fixed test key/value payload and block size. No custom tests beyond inherited suite.

Test signals: Baseline no-codec coverage for the full byte-array TFile contract.
