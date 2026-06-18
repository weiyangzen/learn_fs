## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/ChecksumFs.java

Purpose: `AbstractFileSystem`/`FileContext` counterpart to `ChecksumFileSystem`, wrapping an `AbstractFileSystem` with client-side `.crc` file generation and verification.

Important APIs and types: extends `FilterFs`; exposes `getRawFs`, `getChecksumFile`, `isChecksumFile`, `getChecksumFileLength`, `getBytesPerSum`, `open`, `createInternal`, `setReplication`, `renameInternal`, `delete`, `listStatus`, `listLocatedStatus`, and `reportChecksumFailure`. Internal `ChecksumFSInputChecker` and `ChecksumFSOutputSummer` mirror the `FileSystem` implementation.

Control flow: constructor reads default bytes-per-checksum from raw FS server defaults. Open creates a checksum input checker that reads the raw data stream and corresponding checksum stream, validates header and chunk size, and verifies CRC32 chunks. Create builds data and checksum outputs through raw `createInternal`, writing checksum header and chunk CRCs. Rename/delete/setReplication coordinate data file and checksum file operations. Listings filter checksum files from array and iterator results.

State and persistence behavior: persistent state is raw FS data plus hidden `.crc` siblings. Runtime state includes `defaultBytesPerChecksum`, `verifyChecksum`, and stream-local data/checksum handles.

Dependencies and integration points: integrates with `AbstractFileSystem`, `FilterFs`, `FileContext` flows, `FSInputChecker`, `FSOutputSummer`, `DataChecksum`, permissions, `CreateFlag`, and `ChecksumOpt`.

Risks: same paired-file non-atomicity as `ChecksumFileSystem`. It has no write-checksum disable knob and lacks the newer vectored read and builder overrides present in `ChecksumFileSystem`. `seekToNewSource` assumes `sums` is non-null; missing checksum behavior plus source switching should be tested. Raw FS implementations that already checksum internally can lead to layered checksumming.

Test signals: cover raw server-default checksum size, create/read verification, missing checksum file, corrupt checksum file, rename overwrite/non-overwrite, directory vs file delete, listing filters, replication propagation, EOF seek/skip bounds, and source switching on checksum failure.
