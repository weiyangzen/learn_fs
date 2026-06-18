# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/store/DataBlocks.java

Purpose: upload-buffer abstraction for filesystem output streams, supporting heap byte arrays, direct byte buffers, and temporary disk files as multipart/block upload staging backends.

Important APIs, types, and functions: constants for backend names, `validateWriteArgs()`, `createFactory()`, `BlockUploadData`, abstract `BlockFactory`, abstract `DataBlock`, and concrete array, byte-buffer, and disk factories/blocks.

Control flow: callers choose a factory by configuration name. A `DataBlock` starts in `Writing`, accepts bounded writes until full, transitions through `startUpload()` into `Upload`, and later closes into `Closed`. Array blocks hand off a `ByteArrayInputStream`; byte-buffer blocks flip a direct buffer into a `ByteBufferInputStream`; disk blocks flush/close a temp file and return it as upload data. `BlockUploadData.close()` closes streams, clears cached arrays, and deletes file-backed buffers.

State and persistence: each block tracks state, index, size/capacity, and optional allocation statistics. Disk blocks create local temporary files and delete them during cleanup. ByteBuffer blocks borrow from `DirectBufferPool` and must return buffers on close.

Dependencies and integration points: depends on Hadoop configuration, `LocalDirAllocator`, `DirectBufferPool`, commons IO, Hadoop IO cleanup, and `BlockUploadStatistics`. Used by object-store output stream implementations such as S3A multipart upload buffering.

Risks and test signals: resource cleanup is the main risk: disk temp files and direct buffers must be released exactly once across success and failure paths. Tests should cover state transitions, write bounds, close-before-upload, close-after-upload, byte-array caching, disk file deletion, direct-buffer outstanding count, and invalid backend names.
