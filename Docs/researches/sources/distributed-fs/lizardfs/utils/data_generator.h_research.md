# sources/distributed-fs/lizardfs/utils/data_generator.h

Purpose: deterministic file generator and validator used by LizardFS tests. It creates files whose first 8 bytes store total size in big-endian form and whose body is a predictable sequence of big-endian 64-bit values derived from offset and optional seed.

Important APIs/types/functions: `DataGenerator(seed)` controls deterministic content. `createFile()` creates/truncates and fills a file. `overwriteFile()` preserves existing size and rewrites content. `validateFile(fd,name,file_size)` validates header, size, and body. `validateFile(name,repeat_after_ms)` optionally validates once, sleeps, and validates again to exercise caches. `validateGrowingFile()` validates only the requested current size. Protected helpers fill aligned and unaligned buffers with expected data.

Control flow: generation writes the serialized size, then loops with `UtilsConfiguration::blockSize()` buffers. Validation stats the file, optionally reads and compares the embedded expected size, then uses `pread` at successive offsets and `memcmp` for fast comparison. On mismatch it locates the first bad byte and reports expected/actual hex context.

State and persistence: file contents are the only persistent state. The seed is stored in the object; random seeded mode calls `std::srand(seed_)` inside buffer filling, making output deterministic for a given seed and offset but not thread-safe.

Dependencies/integration: depends on POSIX `open`, `write`, `pread`, `stat`, endian helpers, LizardFS assertion utilities, and `UtilsConfiguration`. It is shared by file generation, overwrite, and validation utilities.

Risks and test signals: files smaller than 8 bytes are invalid for generation. `validateFile(fd,name,file_size)` has subtle behavior when `file_size` is nonzero: it skips header size validation and allows short reads while decrementing by `bytes_read`, so EOF handling must be tested carefully for growing files. Test signals are seeded/unseeded generation, unaligned last blocks, mismatch diagnostics, repeated validation, and cache/race behavior for growing files.
