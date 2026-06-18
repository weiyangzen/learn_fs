# Research: subset-b-000084

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/ioutils/bytespipe_test.go -->
# sources/cloud-native/containers-storage/pkg/ioutils/bytespipe_test.go

Purpose: tests and benchmarks the `ioutils.BytesPipe` queue-like `io.ReadWriteCloser`. The file validates ordering, chunked reads/writes, close behavior, and throughput assumptions for the in-memory pipe.

Important APIs, types, and functions: `TestBytesPipeRead`, `TestBytesPipeWrite`, `TestBytesPipeWriteRandomChunks`, `BenchmarkBytesPipeWrite`, and `BenchmarkBytesPipeRead`. The tests exercise `NewBytesPipe`, `Write`, `Read`, and `Close` and inspect internal buffer state because the test package is `ioutils`.

Control flow: fixed tests write known byte sequences and read them back in smaller chunks. The randomized chunk test computes an expected SHA-1 hash from deterministic write chunking, starts a reader goroutine with delayed start and variable read sizes, writes multiple batches, closes the pipe, and compares hashes.

State and persistence: no persistence. The tests stress transient buffer state, pooled fixed buffers, `bufLen`, and close-driven EOF. The random test depends on goroutine synchronization through a `done` channel.

Dependencies and integration points: depends on `crypto/sha1`, `encoding/hex`, `math/rand/v2`, `time`, `testing`, and `testify/require`. It indirectly covers `bytespipe.go` and the fixed-buffer implementation used by package consumers that need producer/consumer byte buffering.

Risks and edge cases: the random test ignores read errors and stops only on `n == 0`, so it is focused on byte preservation rather than exact terminal errors. Timing delay introduces concurrency coverage but can be nondeterministic. The benchmark write reader goroutine runs until read error and relies on `Close`.

Test signals: coverage confirms FIFO ordering, partial reads, write coalescing into buffers, concurrent read/write with uneven speeds, and performance under repeated writes and reads.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/ioutils/bytespipe_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/ioutils/fswriters.go -->
# sources/cloud-native/containers-storage/pkg/ioutils/fswriters.go

Purpose: provides atomic file-writing primitives for single files and sets of files. It writes data to temporary files or directories, syncs data where configured, then publishes state with `os.Rename`.

Important APIs, types, and functions: `AtomicFileWriterOptions`, `CommittableWriter`, `SetDefaultOptions`, `NewAtomicFileWriterWithOpts`, `NewAtomicFileWriter`, `AtomicWriteFileWithOpts`, `AtomicWriteFile`, `atomicFileWriter.Write/Close/Commit`, `AtomicWriteSet`, `NewAtomicWriteSet`, `WriteFile`, `FileWriter`, `Cancel`, and `Commit`.

Control flow: `newAtomicFileWriter` creates a temp file in the destination directory and records an absolute final path. `Write` records the first write error. `Close` auto-commits unless `ExplicitCommit` is set; `Commit` always requests publishing. Commit syncs data, captures mtime, chmods, optionally full-syncs, closes for platforms that require it, and renames only if no write error was recorded. `AtomicWriteSet` stages files under a temporary root and commits by renaming that whole root to a target directory.

State and persistence: the persistent state is the destination file or target directory made visible by rename. Temporary files and write-set roots are cleanup-sensitive; failed writes remove temp files, and canceled write sets remove the staging tree. `AtomicFileWriterOptions.ModTime` is populated after successful close in `AtomicWriteFileWithOpts`.

Dependencies and integration points: depends on `io`, `os`, `filepath`, and `time`; OS-specific sync behavior is implemented by `fswriters_linux.go` and `fswriters_other.go`. Consumers use this for crash-resistant metadata/config writes in containers-storage.

Risks and edge cases: `defaultWriterOptions` is global mutable state. The `syncFileCloser.Close` logic appears inverted relative to its comment: it closes directly when `NoSync` is false and syncs when `NoSync` is true. `FileWriter` does not create parent directories inside the write set. Concurrent write/close is documented unsupported.

Test signals: `fswriters_test.go` covers atomic write content/mode, explicit commit versus rollback, auto-commit close, write-set commit visibility, and cancel cleanup.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/ioutils/fswriters.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/ioutils/fswriters_linux.go -->
# sources/cloud-native/containers-storage/pkg/ioutils/fswriters_linux.go

Purpose: supplies Linux-specific durability hooks for `atomicFileWriter` and write-set file closers.

Important APIs, types, and functions: `dataOrFullSync`, `(*atomicFileWriter).postDataWrittenSync`, and `(*atomicFileWriter).preRenameSync`.

Control flow: `dataOrFullSync` and `postDataWrittenSync` call `unix.Fdatasync` on the file descriptor unless `NoSync` skips the atomic writer's sync. `preRenameSync` is a no-op because Linux can flush data without doing a full file sync before rename.

State and persistence: affects how staged file contents reach stable storage before rename. It does not itself persist metadata beyond what the caller does with chmod, close, and rename.

Dependencies and integration points: depends on `os` and `golang.org/x/sys/unix`. It is selected on Linux and is called from `fswriters.go` during atomic commits and write-set close wrappers.

Risks and edge cases: fdatasync flushes data and required metadata but not every directory-entry guarantee; callers needing directory fsync are not covered here. Errors propagate and abort commit before rename.

Test signals: Linux behavior is indirectly exercised by `fswriters_test.go`; durability itself is not crash-tested, only functional content and mode behavior are verified.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/ioutils/fswriters_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/ioutils/fswriters_other.go -->
# sources/cloud-native/containers-storage/pkg/ioutils/fswriters_other.go

Purpose: provides non-Linux sync hooks for the atomic file writer.

Important APIs, types, and functions: `dataOrFullSync`, `(*atomicFileWriter).postDataWrittenSync`, and `(*atomicFileWriter).preRenameSync`.

Control flow: `dataOrFullSync` calls `f.Sync`. `postDataWrittenSync` does nothing because platforms such as macOS and Windows may require a full sync instead. `preRenameSync` performs the full sync unless `NoSync` is set.

State and persistence: controls how staged file data is pushed to storage before publishing with rename on non-Linux systems. It does not manage directory-level persistence.

Dependencies and integration points: depends only on `os` and is selected for `!linux`. `fswriters.go` calls these methods through the same `atomicFileWriter` path used on all platforms.

Risks and edge cases: full file sync can be more expensive than Linux fdatasync. Platform differences around rename-after-open are handled by closing in common code before rename. The behavior relies on `os.File.Sync` mapping to the correct platform primitive.

Test signals: cross-platform functional tests in `fswriters_test.go` verify commit semantics and file modes, but not power-loss durability.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/ioutils/fswriters_other.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/ioutils/fswriters_test.go -->
# sources/cloud-native/containers-storage/pkg/ioutils/fswriters_test.go

Purpose: validates atomic single-file and write-set behavior from `fswriters.go`.

Important APIs, types, and functions: `TestAtomicWriteToFile`, `TestAtomicCommitAndRollbackFile`, `TestAtomicWriteSetCommit`, `TestAtomicWriteSetCancel`, and package-level `testMode`.

Control flow: tests create temporary directories, write expected bytes with atomic helpers, read back content, and check mode. The commit/rollback matrix varies `ExplicitCommit` and explicit `Commit` calls to confirm when old data survives or new data is published. Write-set tests stage a file, verify target absence before commit, then rename the set or cancel it.

State and persistence: tests observe filesystem state in temporary directories: target content, file mode, target directory existence, and removal of staging data after cancel.

Dependencies and integration points: depends on `bytes`, `os`, `filepath`, `runtime`, and `testing`. Windows mode handling relaxes expected permissions to `0666`.

Risks and edge cases: tests do not simulate partial write errors, sync failures, rename failures, missing parent directories inside write sets, or crash recovery. Mode comparison uses exact `st.Mode()` against `testMode`, which assumes no extra mode bits.

Test signals: confirms public API behavior for core success paths and explicit commit semantics across supported OS mode differences.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/ioutils/fswriters_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/ioutils/readers.go -->
# sources/cloud-native/containers-storage/pkg/ioutils/readers.go

Purpose: defines small reader wrappers for close callbacks, error callbacks, SHA-256 hashing, EOF hooks, and context-cancelable reads.

Important APIs, types, and functions: `NewReadCloserWrapper`, `NewReaderErrWrapper`, `HashData`, `OnEOFReader`, `NewCancelReadCloser`, and methods on `readCloserWrapper`, `readWriteToCloserWrapper`, `readerErrWrapper`, and `cancelReadCloser`.

Control flow: `NewReadCloserWrapper` preserves `io.WriterTo` when the wrapped reader has it. `readerErrWrapper.Read` invokes a callback on any non-nil read error. `HashData` streams into a SHA-256 hash and returns a `sha256:` string. `OnEOFReader` runs its function once on EOF or close. `NewCancelReadCloser` copies the source into an `io.Pipe`; one goroutine transfers bytes, another closes the pipe with the context error when canceled.

State and persistence: no persistence. Runtime state includes once-only callback state in `OnEOFReader.Fn`, pipe reader/writer state, and a private done context for cancelable reads.

Dependencies and integration points: uses `context`, `crypto/sha256`, `encoding/hex`, and `io`. It supports higher-level storage code that needs deterministic cleanup of streamed resources and cancellation of blocking readers.

Risks and edge cases: `NewCancelReadCloser.Close` closes the wrapper with `io.EOF` but does not directly close the underlying reader; the copier goroutine closes it after copy exits. Callback wrappers are not concurrency-protected. `readerErrWrapper` fires on `io.EOF` as well as real errors.

Test signals: `readers_test.go` covers close callback, error callback, no callback on successful read, hash output, and context-deadline cancellation of a perpetual reader.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/ioutils/readers.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/ioutils/readers_test.go -->
# sources/cloud-native/containers-storage/pkg/ioutils/readers_test.go

Purpose: tests reader helper wrappers from `readers.go`.

Important APIs, types, and functions: `errorReader`, `perpetualReader`, `TestReadCloserWrapperClose`, `TestReaderErrWrapperReadOnError`, `TestReaderErrWrapperRead`, `TestHashData`, and `TestCancelReadCloser`.

Control flow: tests build string/error/perpetual readers, wrap them with callbacks, and verify callbacks and returned errors. The cancel test creates a deadline context and reads repeatedly until `context.DeadlineExceeded` is returned by the wrapped pipe.

State and persistence: no persistence. Test state is callback booleans, in-memory readers, and deadline-controlled goroutines.

Dependencies and integration points: uses `context`, `fmt`, `io`, `strings`, `testing`, `time`, and `testify/assert`. It provides regression signals for consumers relying on cleanup callbacks and cancelable streams.

Risks and edge cases: the cancel test relies on timeouts and a perpetual reader, so it exercises cancellation but not early source EOF or explicit close races. It does not cover `OnEOFReader` or `WriterTo` preservation.

Test signals: verifies expected error propagation, callback invocation boundaries, fixed SHA-256 digest formatting, and cancelable reader context error behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/ioutils/readers_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/ioutils/temp_unix.go -->
# sources/cloud-native/containers-storage/pkg/ioutils/temp_unix.go

Purpose: provides the Unix implementation of `TempDir`.

Important APIs, types, and functions: `TempDir(dir, prefix string) (string, error)`.

Control flow: directly delegates to `os.MkdirTemp` and returns its path and error unchanged.

State and persistence: creates a temporary directory on disk, with lifecycle controlled by the caller.

Dependencies and integration points: depends on `os`; selected for all non-Windows builds. It gives package callers a platform-neutral API paired with the Windows long-path implementation.

Risks and edge cases: inherits all `os.MkdirTemp` behavior around permissions, naming, and cleanup. Unlike Windows, no path normalization or long-path prefix is applied.

Test signals: no direct test in the requested set; behavior is simple stdlib delegation and is indirectly used where callers create temp directories.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/ioutils/temp_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/ioutils/temp_windows.go -->
# sources/cloud-native/containers-storage/pkg/ioutils/temp_windows.go

Purpose: provides the Windows implementation of `TempDir` that returns a long-path-safe directory name.

Important APIs, types, and functions: `TempDir(dir, prefix string) (string, error)`.

Control flow: calls `os.MkdirTemp`, returns any creation error, then wraps the resulting path with `longpath.AddPrefix`.

State and persistence: creates a temporary directory on disk; the returned path may include `\\?\` or `\\?\UNC\` to bypass legacy Windows path length limits.

Dependencies and integration points: depends on `os` and `github.com/containers/storage/pkg/longpath`. It is selected only on Windows and aligns temp directory handling with other Windows filesystem helpers.

Risks and edge cases: callers must tolerate long-path-prefixed strings. Cleanup APIs generally accept the prefix, but external tools may not. Directory removal remains caller-owned.

Test signals: covered indirectly by longpath tests for prefix construction; no direct `TempDir` Windows test in the requested files.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/ioutils/temp_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/ioutils/writeflusher.go -->
# sources/cloud-native/containers-storage/pkg/ioutils/writeflusher.go

Purpose: wraps a writer and optional flusher so every write is followed by a flush and close can stop future writes.

Important APIs, types, and functions: `WriteFlusher`, `NewWriteFlusher`, `Write`, `Flush`, `Flushed`, `Close`, the private `flusher` interface, and `errWriteFlusherClosed`.

Control flow: `Write` checks the `closed` channel, writes to the underlying writer, then calls `Flush` regardless of write error. `Flush` closes the `flushed` channel once and invokes the underlying flusher if still open. `Close` uses a mutex to close the `closed` channel once and returns `io.EOF` if already closed.

State and persistence: no persistence. State is channel-based lifecycle tracking plus a `sync.Once` that records the first flush event.

Dependencies and integration points: depends on `io` and `sync`. It integrates with streaming HTTP-like paths where immediate flushing and post-close write suppression are needed. `NopFlusher` from `writers.go` is used when the writer lacks `Flush`.

Risks and edge cases: `Flushed` is explicitly racy and only suitable for weak observation. `Write` flushes even after a partial/error write. `Close` does not close the underlying writer; it only closes the wrapper.

Test signals: no requested direct tests for `WriteFlusher`; behavior should be covered by callers or future tests around flush-on-write and close races.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/ioutils/writeflusher.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/ioutils/writers.go -->
# sources/cloud-native/containers-storage/pkg/ioutils/writers.go

Purpose: provides small writer adapters: no-op writer/closer/flusher, close callback wrapper, and byte-counting writer.

Important APIs, types, and functions: `NopWriter`, `NopWriteCloser`, `NopFlusher`, `NewWriteCloserWrapper`, `WriteCounter`, and `NewWriteCounter`.

Control flow: `NopWriter.Write` discards bytes and reports full length. `NopWriteCloser` delegates writes and makes `Close` a no-op. `NewWriteCloserWrapper` returns a writer with custom close callback. `WriteCounter.Write` delegates to its wrapped writer and accumulates the number of bytes successfully reported.

State and persistence: no persistence. `WriteCounter.Count` is mutable in-memory state and is not concurrency-protected.

Dependencies and integration points: depends on `io`. These helpers are used by higher-level stream plumbing, buffer pools, and code paths needing an `io.WriteCloser` around an existing writer.

Risks and edge cases: no-op writers can mask data loss if used accidentally. `WriteCounter` counts short writes exactly as reported but leaves error handling to callers. Close wrappers do not guard multiple close calls.

Test signals: `writers_test.go` verifies close callback, no-op close/write behavior, byte counting, and actual data forwarding.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/ioutils/writers.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/ioutils/writers_test.go -->
# sources/cloud-native/containers-storage/pkg/ioutils/writers_test.go

Purpose: tests writer adapters from `writers.go`.

Important APIs, types, and functions: `TestWriteCloserWrapperClose`, `TestNopWriteCloser`, `TestNopWriter`, and `TestWriteCounter`.

Control flow: tests wrap in-memory buffers, call close/write paths, and copy data from string readers through `WriteCounter`. Assertions check callbacks, nil close errors, reported byte counts, accumulated count, and final buffer content.

State and persistence: no persistence. State is in-memory buffer contents and a boolean callback flag.

Dependencies and integration points: depends on `bytes`, `strings`, `testing`, and `testify/require`. It verifies utility behavior used by pool wrappers and stream code.

Risks and edge cases: tests do not cover error-returning underlying writers, short writes, multiple closes, or concurrent use. They establish basic adapter contract only.

Test signals: confirms that wrapper plumbing does not drop bytes and `WriteCounter` reflects total written bytes across multiple writes.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/ioutils/writers_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/locker/locker.go -->
# sources/cloud-native/containers-storage/pkg/locker/locker.go

Purpose: implements named in-process locks so callers can serialize work by resource key instead of holding a coarse global mutex.

Important APIs, types, and functions: `Locker`, `New`, `Lock`, `Unlock`, `ErrNoSuchLock`, and private `lockCtr` with atomic waiter count.

Control flow: `Locker.Lock` creates or finds a `lockCtr` under the global map mutex, increments its waiter count while protected, releases the map mutex, then blocks on the per-name mutex and decrements waiters after acquisition. `Unlock` finds the per-name lock, deletes it from the map when no waiters remain, unlocks the per-name mutex while still under the map mutex, and returns an error for unknown names.

State and persistence: state is purely in-memory: a map from lock names to counters and waiter counts. Entries are removed after the final holder unlocks when no waiters exist.

Dependencies and integration points: depends on `errors`, `sync`, and `sync/atomic`. It is suitable for process-local resource serialization but does not coordinate across processes.

Risks and edge cases: unlocking an existing but not-held per-name mutex would panic via `sync.Mutex`. Deleting before unlock relies on waiter counts to prevent concurrent lookup races. No fairness guarantee is provided beyond `sync.Mutex`.

Test signals: `locker_test.go` covers waiter counting, blocking behavior, cleanup after unlock, and high-concurrency lock/unlock loops.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/locker/locker.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/locker/locker_test.go -->
# sources/cloud-native/containers-storage/pkg/locker/locker_test.go

Purpose: tests the named-lock manager in `locker.go`.

Important APIs, types, and functions: `TestLockCounter`, `TestLockerLock`, `TestLockerUnlock`, and `TestLockerConcurrency`.

Control flow: tests increment/decrement counters, acquire a lock and verify a second goroutine blocks until unlock, confirm a released lock can be acquired again, and run 10001 goroutines that lock and unlock the same name.

State and persistence: no persistence. The tests inspect `Locker.locks` and `lockCtr.waiters` directly because they are in package scope.

Dependencies and integration points: depends on `sync`, `testing`, `time`, and `testify/require`. It validates expected behavior for users relying on key-scoped in-process locking.

Risks and edge cases: time-based waiting uses polling and timeouts. Tests do not check unknown unlock error or unlocking without a matching lock holder.

Test signals: confirms waiter counts, blocking semantics, release cleanup, and absence of obvious data races or panics under many goroutines.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/locker/locker_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/lockfile/lastwrite.go -->
# sources/cloud-native/containers-storage/pkg/lockfile/lastwrite.go

Purpose: defines the opaque `LastWrite` token stored in lock files to detect changes to protected state across goroutines and processes.

Important APIs, types, and functions: `LastWrite`, `newLastWrite`, `serialize`, `equals`, `newLastWriteFromData`, `lastWriterIDCounter`, and `lastWriterIDSize`.

Control flow: `newLastWrite` builds a 64-byte token from current time, an atomic per-process counter, PID, and random bytes. `serialize` and `equals` panic on uninitialized values to enforce opaque value semantics. `newLastWriteFromData` wraps bytes read from a lock file.

State and persistence: tokens are persisted as raw lock-file contents by OS-specific `RecordWrite`. In-process state includes the atomic counter used to reduce collision risk.

Dependencies and integration points: depends on `bytes`, `crypto/rand`, `encoding/binary`, `os`, `sync/atomic`, and `time`. It integrates with `LockFile.GetLastWrite`, `RecordWrite`, and `ModifiedSince`.

Risks and edge cases: random failure panics. `newLastWriteFromData` does not copy the slice, so callers should not mutate the source bytes. Equality ignores semantic structure and compares raw bytes.

Test signals: lockfile tests exercise `RecordWrite`, `GetLastWrite`, `Modified`, and `ModifiedSince`, indirectly validating token uniqueness and comparison.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/lockfile/lastwrite.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/lockfile/lockfile.go -->
# sources/cloud-native/containers-storage/pkg/lockfile/lockfile.go

Purpose: implements process-local and inter-process lock-file coordination with read/write locks and last-writer tracking.

Important APIs, types, and functions: `Locker` interface, `LockFile`, `GetLockFile`, `GetROLockFile`, deprecated `GetLockfile`/`GetROLockfile`, `Lock`, `RLock`, `TryLock`, `TryRLock`, `Unlock`, `AssertLocked`, `AssertLockedForWriting`, `ModifiedSince`, `Modified`, `Touch`, `IsReadWrite`, `openLock`, `createLockFileForPath`, `lock`, and `tryLock`.

Control flow: lock objects are cached by absolute path and read-only mode. Acquisition first takes an in-process `sync.RWMutex`; on the first nested lock it opens the lock file and calls `rawfilelock.LockFile` or `TryLockFile`. Nested locks increment `counter` and reuse the fd. Unlock decrements, releases the raw file lock and closes the handle when the counter reaches zero, then releases the in-process RW lock. Last-write checks require the caller to hold the lock.

State and persistence: persistent state is the lock file contents storing the last-write token. In-memory state includes cached `LockFile` objects, lock counters, current fd, lock type, and compatibility `lw` for deprecated `Modified`.

Dependencies and integration points: depends on `fmt`, `os`, `filepath`, `sync`, `time`, and `github.com/containers/storage/internal/rawfilelock`. OS-specific files implement last-write read/write and timestamp checks.

Risks and edge cases: many misuse cases intentionally panic: write-locking a read-only lock, unlocking an unlocked lock, checking or recording without the right lock. Cached lock mode mismatches return errors. If raw lock acquisition panics in `lock`, callers must recover at a higher level. `AssertLocked` cannot identify ownership by goroutine.

Test signals: `lockfile_test.go` covers in-process, try-lock, multiprocess read/write/mixed locking, last-write detection, and read-only panic behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/lockfile/lockfile.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/lockfile/lockfile_test.go -->
# sources/cloud-native/containers-storage/pkg/lockfile/lockfile_test.go

Purpose: integration-heavy tests for lock-file concurrency, reexec child processes, and last-write detection.

Important APIs, types, and functions: `TestMain`, `subTouchMain`, `subLockMain`, `subRLockMain`, `subTouch`, `subLock`, `subRLock`, `getTempLockfile`, and tests for try locks, read/write locks, multiprocess locking, `Touch`, `RecordWrite`, `Modified`, and `ModifiedSince`.

Control flow: helper subprocesses are registered through `reexec`; children acquire a lock, close stdout to signal acquisition, wait for stdin closure, then unlock or touch. Tests coordinate with pipes to verify blocking and cross-process behavior. Concurrent tests use counters to detect simultaneous writers or writer/reader overlap.

State and persistence: tests create real temporary lock files and observe persisted last-write token changes and file mtimes. In-memory counters track critical-section overlap.

Dependencies and integration points: depends on `io`, `os`, `os/exec`, `runtime`, `sync`, `sync/atomic`, `testing`, `time`, `reexec`, `logrus`, and `testify`. It validates the `lockfile` package against actual platform file locking.

Risks and edge cases: tests can be slow due to sleeps and many subprocesses/goroutines. Some tests depend on platform lock semantics and timer granularity. Comments note coverage is not exhaustive.

Test signals: strong signals for exclusive writers, shared readers, mixed read/write exclusion, try-lock failure, read-only write panic, timestamp touching, and external modification detection.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/lockfile/lockfile_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/lockfile/lockfile_unix.go -->
# sources/cloud-native/containers-storage/pkg/lockfile/lockfile_unix.go

Purpose: implements Unix last-write and touch-time operations for `LockFile`.

Important APIs, types, and functions: `GetLastWrite`, `RecordWrite`, and `TouchedSince`.

Control flow: `GetLastWrite` uses `unix.Pread` at offset zero into a fixed-size buffer and accepts partial reads for new empty lock files. `RecordWrite` creates a new token and writes it at offset zero with `unix.Pwrite`, returning `ENOSPC` on short write. `TouchedSince` reads fd metadata through `system.Fstat` and compares mtime to the provided time.

State and persistence: persists the last-write token directly in the lock file without changing current fd offset. Timestamp checks reflect filesystem metadata on the open lock handle.

Dependencies and integration points: depends on `time`, `github.com/containers/storage/pkg/system`, and `golang.org/x/sys/unix`. Called only while the common `LockFile` asserts the correct lock is held.

Risks and edge cases: partial initial reads are valid and produce a shorter token. Short writes are treated as disk-full. Timestamp comparison truncates through `time.Unix(mtim.Unix())`, so nanosecond precision is not retained.

Test signals: Unix/Linux lockfile tests cover `Touch`, `RecordWrite`, `ModifiedSince`, and `TouchedSince` behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/lockfile/lockfile_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/lockfile/lockfile_windows.go -->
# sources/cloud-native/containers-storage/pkg/lockfile/lockfile_windows.go

Purpose: implements Windows last-write and touch-time operations for `LockFile`.

Important APIs, types, and functions: constants `reserved` and `allBytes`, plus `GetLastWrite`, `RecordWrite`, and `TouchedSince`.

Control flow: `GetLastWrite` reads from the file handle using `windows.ReadFile` with an overlapped structure and treats EOF as a valid empty initial lock. `RecordWrite` writes a new token with `windows.WriteFile` and returns disk-full on short write. `TouchedSince` uses `os.Stat` on the lock path and compares mtime.

State and persistence: persists token bytes in the Windows lock file. Timestamp state is observed through path metadata rather than fd stat.

Dependencies and integration points: depends on `os`, `time`, and `golang.org/x/sys/windows`. It implements the methods called by common `lockfile.go` under Windows builds.

Risks and edge cases: callers must use the common lock acquisition path before invoking these methods. Windows handle and overlapped semantics differ from Unix and are only lightly covered by platform-specific tests.

Test signals: Windows-specific behavior is not covered in the requested test file, but common lockfile tests can run on Windows when the underlying raw lock implementation supports them.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/lockfile/lockfile_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/longpath/longpath.go -->
# sources/cloud-native/containers-storage/pkg/longpath/longpath.go

Purpose: provides Windows long-path prefix handling.

Important APIs, types, and functions: `Prefix` and `AddPrefix`.

Control flow: `AddPrefix` returns the input unchanged if it already starts with `\\?\`. For UNC paths beginning with `\\`, it converts them to `\\?\UNC\server\share...`; all other paths receive `\\?\` directly.

State and persistence: no state or persistence; it only transforms path strings.

Dependencies and integration points: depends on `strings`. Used by Windows temp directory handling and other filesystem code that must support paths beyond legacy limits.

Risks and edge cases: it is purely syntactic and does not validate absolute paths, drive letters, or malformed UNC strings. Applying it on non-Windows paths would produce Windows-specific strings.

Test signals: `longpath_test.go` validates normal drive-letter and UNC path conversions.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/longpath/longpath.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/longpath/longpath_test.go -->
# sources/cloud-native/containers-storage/pkg/longpath/longpath_test.go

Purpose: tests Windows long-path prefix conversion.

Important APIs, types, and functions: `TestStandardLongPath` and `TestUNCLongPath`.

Control flow: each test calls `AddPrefix` with a representative drive-letter or UNC path and compares with the expected long-path form using case-insensitive comparison.

State and persistence: no state or persistence; only string transformations are checked.

Dependencies and integration points: depends on `strings` and `testing`. It verifies behavior consumed by Windows filesystem helpers such as `ioutils.TempDir`.

Risks and edge cases: tests do not cover already-prefixed paths, relative paths, malformed UNC paths, or empty strings.

Test signals: confirms the two main supported Windows path shapes are mapped correctly.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/longpath/longpath_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/loopback/attach_loopback.go -->
# sources/cloud-native/containers-storage/pkg/loopback/attach_loopback.go

Purpose: attaches a sparse backing file to an available Linux loop device.

Important APIs, types, and functions: errors `ErrAttachLoopbackDevice`, `ErrGetLoopbackBackingFile`, `ErrSetCapacity`; `stringToLoopName`, `getNextFreeLoopbackIndex`, `openNextAvailableLoopback`, `AttachLoopDevice`, `AttachLoopDeviceRO`, and `attachLoopDevice`.

Control flow: the code opens `/dev/loop-control`, asks for a free index, opens `/dev/loopN`, verifies it is a block device, calls `LOOP_SET_FD`, verifies backing device/inode, then sets loop status with autoclear. It loops around races where another process grabs a device or the kernel reports ENXIO/EBUSY.

State and persistence: persistent kernel state is the loop device association with the backing file. `LO_FLAGS_AUTOCLEAR` asks the kernel to detach on last close. The sparse file is opened temporarily; the returned loop `*os.File` is caller-owned.

Dependencies and integration points: depends on `errors`, `fmt`, `io/fs`, `os`, `syscall`, `logrus`, and `x/sys/unix`. It uses ioctl wrappers and constants from sibling files.

Risks and edge cases: requires Linux loop device permissions. Race handling is bounded to 1000 attempts. Read-only mode opens the backing file read-only but does not set `LO_FLAGS_READ_ONLY`, which may matter for strict RO expectations. Verification mismatch logs but does not fail.

Test signals: `attach_test.go` stress-tests concurrent attachment on Linux when sufficient privileges/devices exist.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/loopback/attach_loopback.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/loopback/attach_test.go -->
# sources/cloud-native/containers-storage/pkg/loopback/attach_test.go

Purpose: stress-tests Linux loopback attachment under concurrent races.

Important APIs, types, and functions: constants `maxDevicesPerGoroutine`, `maxGoroutines`, and `TestAttachLoopbackDeviceRace`.

Control flow: the test starts multiple goroutines; each repeatedly creates a temporary backing file, calls `AttachLoopDevice`, asserts success and non-nil result, closes the loop file, and removes the backing file.

State and persistence: creates many temporary files and transient loop-device associations with autoclear cleanup through file close.

Dependencies and integration points: depends on `os`, `sync`, `testing`, and `testify`. It exercises kernel loop-control integration rather than only wrapper logic.

Risks and edge cases: requires Linux, loop devices, and enough permissions, so it may fail or be skipped by environment policy elsewhere. With 10,000 attempts it can be slow and resource-intensive.

Test signals: high-value race signal for EBUSY/ENXIO retry logic and autoclear loop lifecycle under parallel attach/close.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/loopback/attach_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/loopback/ioctl.go -->
# sources/cloud-native/containers-storage/pkg/loopback/ioctl.go

Purpose: wraps Linux loop-device ioctls behind small typed Go functions.

Important APIs, types, and functions: `ioctlLoopCtlGetFree`, `ioctlLoopSetFd`, `ioctlLoopSetStatus64`, `ioctlLoopClrFd`, `ioctlLoopGetStatus64`, and `ioctlLoopSetCapacity`.

Control flow: each function invokes `syscall.Syscall` with `SYS_IOCTL`, the fd, an ioctl request constant, and an optional argument. Non-zero errno is returned as an error; successful get-status returns a populated `loopInfo64`.

State and persistence: changes or queries kernel loop device state. `SET_FD`, `SET_STATUS64`, `CLR_FD`, and `SET_CAPACITY` mutate kernel state; `GET_STATUS64` and `CTL_GET_FREE` query it.

Dependencies and integration points: depends on `syscall` and `unsafe`; uses constants and struct layout from `loop_wrapper.go`. Called by attach, find, and capacity helpers.

Risks and edge cases: unsafe pointer layout must match the kernel ABI. `syscall.Syscall` is Linux-specific and build-tagged. Callers must pass valid fds and handle permission failures.

Test signals: indirectly covered by loopback attachment and capacity/find behavior; no direct unit tests mock ioctl results.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/loopback/ioctl.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/loopback/loop_wrapper.go -->
# sources/cloud-native/containers-storage/pkg/loopback/loop_wrapper.go

Purpose: defines Go-side Linux loop ioctl ABI structures and constants.

Important APIs, types, and functions: `loopInfo64` and constants `LoopSetFd`, `LoopCtlGetFree`, `LoopGetStatus64`, `LoopSetStatus64`, `LoopClrFd`, `LoopSetCapacity`, `LoFlagsAutoClear`, `LoFlagsReadOnly`, `LoFlagsPartScan`, `LoKeySize`, and `LoNameSize`.

Control flow: no runtime control flow; this file maps `x/sys/unix` constants into package-local names and defines the struct used with unsafe ioctl calls.

State and persistence: no state itself, but its layout controls how kernel loop status is read and written by `ioctl.go`.

Dependencies and integration points: depends on `golang.org/x/sys/unix`. `attach_loopback.go`, `ioctl.go`, and `loopback.go` rely on these constants and fields.

Risks and edge cases: ABI mismatch would corrupt ioctl calls. Field names are unexported, so only package code can manipulate them.

Test signals: validated only through real Linux loopback operations; no compile-time ABI assertion is present.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/loopback/loop_wrapper.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/loopback/loopback.go -->
# sources/cloud-native/containers-storage/pkg/loopback/loopback.go

Purpose: provides Linux helpers for querying, resizing, and finding loop devices by backing file.

Important APIs, types, and functions: `getLoopbackBackingFile`, `SetCapacity`, and `FindLoopDeviceFor`.

Control flow: `getLoopbackBackingFile` calls `LOOP_GET_STATUS64` and returns backing device/inode. `SetCapacity` calls `LOOP_SET_CAPACITY`. `FindLoopDeviceFor` stats the backing file, scans `/dev/loop0`, `/dev/loop1`, and so on until first non-existent loop device, returning the open loop file whose backing device/inode matches.

State and persistence: interacts with kernel loop-device state. `SetCapacity` updates the kernel's view of the loop device size. `FindLoopDeviceFor` returns an open file descriptor that the caller must close.

Dependencies and integration points: depends on `fmt`, `os`, `syscall`, and `logrus`; uses ioctl wrappers from this package.

Risks and edge cases: scanning stops at the first missing `/dev/loopN`, so sparse loop numbering could miss later devices. Non-not-exist open errors are ignored. Returned matched loop file stays open.

Test signals: no direct requested test for `FindLoopDeviceFor` or `SetCapacity`; attach tests exercise backing-file status reads indirectly.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/loopback/loopback.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/loopback/loopback_unsupported.go -->
# sources/cloud-native/containers-storage/pkg/loopback/loopback_unsupported.go

Purpose: declares the `loopback` package for unsupported builds.

Important APIs, types, and functions: no functions or types are defined in this file.

Control flow: none.

State and persistence: none.

Dependencies and integration points: package declaration only. Because the Linux files carry explicit build tags, this file allows the package to exist on other platforms without loopback APIs.

Risks and edge cases: callers expecting loopback functions on non-Linux platforms will not compile unless guarded by build tags or platform-specific files.

Test signals: no tests; the signal is successful non-Linux package compilation where no loopback implementation is intended.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/loopback/loopback_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/mflag/example/example.go -->
# sources/cloud-native/containers-storage/pkg/mflag/example/example.go

Purpose: demonstrates the custom `mflag` command-line parser, including aliases, deprecated/hidden names, boolean flags, string/int flags, and help output.

Important APIs, types, and functions: package-level variables `i`, `str`, `b`, `b2`, `h`; `init` flag registrations; and `main` output logic.

Control flow: `init` registers several flags with names prefixed by `#` for hidden/deprecated behavior and calls `flag.Parse`. `main` prints defaults when help was requested, otherwise prints parsed values and remaining args.

State and persistence: no persistence. Program state is command-line flag values held in package variables and the global `mflag.CommandLine` set.

Dependencies and integration points: depends on `fmt` and `github.com/containers/storage/pkg/mflag`. It is an executable example for developers using `mflag`.

Risks and edge cases: parsing during `init` makes this example unsuitable as an importable helper. Some registered variables share the same destination pointer, intentionally demonstrating aliases but also showing how names can overwrite the same value.

Test signals: no tests; behavior is illustrative and complements `flag_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/mflag/example/example.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/mflag/flag.go -->
# sources/cloud-native/containers-storage/pkg/mflag/flag.go

Purpose: implements a Docker-derived command-line flag package with multiple names per flag, deprecated/hidden names, grouped short booleans, argument-count validation, and flag-set merging.

Important APIs, types, and functions: value types for bool/int/int64/uint/uint64/uint16/string/float64/duration; `Value`, `Getter`, `ErrorHandling`, `FlagSet`, `Flag`; top-level `CommandLine`; registration methods like `BoolVar`, `Int`, `String`, `Duration`; lookup/visit/set helpers; `Parse`, `ParseFlags`, `ReportError`, `Require`, `CheckArgs`, `Merge`, and `IsEmpty`.

Control flow: flags are registered in `formal` under every normalized name, with `#` stripped for lookup but retained in `Flag.Names` to hide/deprecate usage output. `parseOne` consumes one flag, splits `name=value`, strips quotes, handles implicit boolean true, consumes following args for non-bools, emits deprecation warnings, and records `actual`. Unknown multi-letter names return `ErrRetry`, causing `Parse` to retry letter-by-letter for grouped short flags.

State and persistence: no persistence. State lives in `FlagSet`: parsed args, formal definitions, actual values, output writer, and argument requirements. Top-level helpers mutate the global `CommandLine`.

Dependencies and integration points: depends on stdlib parsing/formatting packages and `homedir` for usage path shortening. Used by CLI entry points needing Docker-compatible flag behavior.

Risks and edge cases: not concurrency-safe. `ShortUsage` writes to `CommandLine.output` directly and can be nil. `ParseFlags` exits the process on help or bad args. Grouped-short retry can produce surprising behavior for unknown multi-letter flags. Duplicate names panic in `Var`.

Test signals: `flag_test.go` covers all built-in value types, parsing forms, quotes, help, count functions, deprecated/hidden names, grouped flags, user-defined values, merge behavior, output routing, and argument requirements.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/mflag/flag.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/mflag/flag_test.go -->
# sources/cloud-native/containers-storage/pkg/mflag/flag_test.go

Purpose: tests the custom `mflag` package behavior across value types, parsing modes, errors, usage, and merging.

Important APIs, types, and functions: `ResetForTesting`, `TestEverything`, `TestGet`, `testParse`, `TestParse`, `TestFlagSetParse`, `TestUserDefined`, `TestUserDefinedBool`, `TestSetOutput`, `TestChangingArgs`, `TestHelp`, `TestFlagCounts`, `TestSortFlags`, `TestMergeFlags`, and helper custom value types.

Control flow: tests reset the global command line, define flags, parse synthetic arg lists, inspect resulting pointer values and set state, and validate visitor ordering. User-defined tests verify repeated custom values and bool-like custom values. Help and output tests check special parse paths.

State and persistence: no persistence. Tests mutate global `CommandLine`, `os.Args`, and in-memory `FlagSet` maps.

Dependencies and integration points: depends on `bytes`, `fmt`, `os`, `sort`, `strings`, `testing`, `time`, and `testify`. It protects command-line compatibility for consumers using `mflag`.

Risks and edge cases: tests intentionally manipulate globals, so isolation depends on `ResetForTesting` and deferred restoration. Process-exit paths in `ParseFlags` are not directly exercised.

Test signals: broad coverage for parsing syntax, quoting, typed getters, grouped short flags, deprecation counting, sorting idempotence, merge forwarding, and custom value semantics.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/mflag/flag_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/mount/flags.go -->
# sources/cloud-native/containers-storage/pkg/mount/flags.go

Purpose: translates fstab-style mount option strings into platform mount flags and filesystem-specific data.

Important APIs, types, and functions: maps `flags`, `validFlags`, `propagationFlags`; functions `MergeTmpfsOptions`, `ParseOptions`, and `ParseTmpfsOptions`.

Control flow: `ParseOptions` splits comma options, sets or clears known flags, and passes unknown/unsupported options through as data. `ParseTmpfsOptions` validates data keys against tmpfs allowed keys. `MergeTmpfsOptions` walks options in reverse so later options win, removes defaults and duplicates, collapses mutually exclusive flag/data settings, and returns an error for invalid tmpfs keys.

State and persistence: no persistence. State is static option metadata and returned flag/data values.

Dependencies and integration points: depends on `fmt` and `strings`; constants come from OS-specific flag files. Used by `Mount`, `ForceMount`, tmpfs callers, and mount tests.

Risks and edge cases: unsupported platform constants are zero, so known but zero-valued options become data rather than flags. `ParseOptions` does not validate generic unknown data. Propagation flags collide under key `-1`, so only the latest propagation option survives in tmpfs merge.

Test signals: `mount_unix_test.go` checks basic parsing and tmpfs option merging/error behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/mount/flags.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/mount/flags_freebsd.go -->
# sources/cloud-native/containers-storage/pkg/mount/flags_freebsd.go

Purpose: maps mount flag constants to FreeBSD `unix.MNT_*` values and zeroes unsupported Linux-style flags.

Important APIs, types, and functions: constants `RDONLY`, `NOSUID`, `NOEXEC`, `SYNCHRONOUS`, `REMOUNT`, `NOATIME`, `mntDetach`, and zero-valued unsupported flags such as `BIND`, `RPRIVATE`, and `RELATIME`.

Control flow: no runtime flow; constants are used by option parsing and mount/unmount wrappers.

State and persistence: no state. The constants influence kernel mount calls on FreeBSD.

Dependencies and integration points: depends on `golang.org/x/sys/unix`; selected for FreeBSD builds. Integrated with `flags.go`, `mounter_freebsd.go`, and `unmount_unix.go`.

Risks and edge cases: Linux-specific options silently become data or no-ops because constants are zero. FreeBSD bind behavior is emulated in `mounter_freebsd.go` via `nullfs`.

Test signals: no FreeBSD-specific tests in the requested files; correctness is mostly compile-time plus platform integration tests elsewhere.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/mount/flags_freebsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/mount/flags_linux.go -->
# sources/cloud-native/containers-storage/pkg/mount/flags_linux.go

Purpose: maps package mount constants to Linux `unix.MS_*` and unmount constants.

Important APIs, types, and functions: constants for read-only, nosuid, nodev, noexec, sync, dirsync, remount, mandatory lock, atime, bind/rbind, propagation modes, relatime/strictatime, and `mntDetach`.

Control flow: no runtime control flow; constants feed parsing and syscall wrappers.

State and persistence: no state. Values control kernel mount/unmount behavior when passed to `unix.Mount` or `unix.Unmount`.

Dependencies and integration points: depends on `golang.org/x/sys/unix`; selected for Linux. Used by `flags.go`, `mounter_linux.go`, `sharedsubtree_linux.go`, and unmount helpers.

Risks and edge cases: flag combinations can require multi-step mount calls, handled in `mounter_linux.go`. Future kernel options would require updating this map.

Test signals: Linux mount tests validate many combinations of bind, ro/rw, remount, and propagation flags.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/mount/flags_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/mount/flags_unsupported.go -->
# sources/cloud-native/containers-storage/pkg/mount/flags_unsupported.go

Purpose: defines zero-valued mount constants for platforms without Linux or FreeBSD support.

Important APIs, types, and functions: zero constants for all package mount flags and `mntDetach`.

Control flow: none; constants only.

State and persistence: none.

Dependencies and integration points: selected for `!linux && !freebsd`. It lets packages compile even though mount operations are unsupported.

Risks and edge cases: parsing known option names with zero-valued flags treats them as data or no-ops. Actual mount/unmount implementations panic on unsupported platforms.

Test signals: no direct tests; compile coverage on unsupported platforms is the main signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/mount/flags_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/mount/mount.go -->
# sources/cloud-native/containers-storage/pkg/mount/mount.go

Purpose: provides high-level mount and unmount API wrappers plus formatted mount errors.

Important APIs, types, and functions: `mountError`, `Mount`, `ForceMount`, `Unmount`, `RecursiveUnmount`, and deprecated `ForceUnmount`.

Control flow: `Mount` parses options, checks whether the target is already mounted unless this is a remount, then delegates to platform `mount`. `ForceMount` skips the mounted check. `Unmount` and `ForceUnmount` delegate to platform `unmount` with lazy/detach flags. `RecursiveUnmount` reads all mounts, sorts deepest mountpoints first, unmounts descendants under the target, and only returns an error for the final relevant unmount failure.

State and persistence: mutates kernel mount table state through platform calls. No package-level persistent state.

Dependencies and integration points: depends on `sort`, `strconv`, and `strings`; integrates with `mountinfo` for mounted checks and with OS-specific mounter/unmounter files.

Risks and edge cases: `RecursiveUnmount` uses simple string prefix matching, so paths like `/foo2` can match target `/foo` unless callers pass normalized boundaries. Mounted-check races remain possible between check and mount.

Test signals: Linux tests exercise `Mount`, `Unmount`, `Mounted`, read-only bind behavior, and mountinfo visibility.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/mount/mount.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/mount/mount_unix_test.go -->
# sources/cloud-native/containers-storage/pkg/mount/mount_unix_test.go

Purpose: tests Linux mount option parsing and basic mount/unmount integration.

Important APIs, types, and functions: `TestMountOptionsParsing`, `TestMounted`, `TestMountReadonly`, `TestGetMounts`, and `TestMergeTmpfsOptions`.

Control flow: root-only tests create temp source/target directories, bind mount them, check `Mounted`, verify read-only behavior by attempting an RW open, and unmount in defers. Non-root environments skip privileged mount tests.

State and persistence: temporarily mutates the host mount table and filesystem under temp directories; cleanup depends on deferred unmounts and directory removal.

Dependencies and integration points: depends on `os`, `path`, `slices`, `testing`, and `testify/require`. It validates mount parsing and Linux kernel mount integration.

Risks and edge cases: requires root. Defers call `t.Fatal` in cleanup, which can obscure prior failures. Tests do not cover recursive unmount.

Test signals: confirms parser flags/data, `Mounted`/`GetMounts`, bind mount success, read-only bind enforcement, and tmpfs option collision/error handling.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/mount/mount_unix_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/mount/mounter_freebsd.go -->
# sources/cloud-native/containers-storage/pkg/mount/mounter_freebsd.go

Purpose: implements FreeBSD mount operations using `nmount` through cgo.

Important APIs, types, and functions: `allocateIOVecs` and platform `mount`.

Control flow: the function builds a key/value iovec list starting with `fspath`. Data options are split into names and values; a `bind` data option switches to `nullfs` with `target=device`, otherwise it uses the requested filesystem type and `from=device`. It calls `C.nmount` and converts errno to a Go error string.

State and persistence: mutates the FreeBSD mount table. Allocated C strings are freed with defers after the syscall.

Dependencies and integration points: depends on cgo FreeBSD mount headers, `fmt`, `strings`, and `unsafe`. Used by high-level `Mount` on `freebsd && cgo`.

Risks and edge cases: data option parsing assumes `key=value`; options without values still append an empty value. cgo is required. Error wrapping does not use `mountError`, unlike Linux.

Test signals: no FreeBSD tests in the requested set; correctness depends on platform integration.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/mount/mounter_freebsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/mount/mounter_linux.go -->
# sources/cloud-native/containers-storage/pkg/mount/mounter_linux.go

Purpose: implements Linux mount syscall sequencing for normal, bind, remount, read-only bind, and propagation changes.

Important APIs, types, and functions: constants `ptypes`, `pflags`, `broflags`, `none`; functions `isremount` and platform `mount`.

Control flow: `isremount` treats explicit `MS_REMOUNT`, empty device, or `none` device as remount-like. `mount` first applies non-propagation flags and data when appropriate, then applies propagation flags with a second mount call, then remounts bind mounts read-only when `MS_BIND|MS_RDONLY` are both present.

State and persistence: mutates the Linux mount namespace. No package-level state.

Dependencies and integration points: depends on `golang.org/x/sys/unix`; called by `mount.go` and `sharedsubtree_linux.go`.

Risks and edge cases: mount operations are privileged and namespace-sensitive. Multi-step bind read-only setup can leave intermediate state if a later step fails. Treating `device == "none"` as remount supports compatibility but affects call ordering.

Test signals: `mounter_linux_test.go` validates option outcomes in `/proc/self/mountinfo` across bind, propagation, read-only, and remount scenarios.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/mount/mounter_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/mount/mounter_linux_test.go -->
# sources/cloud-native/containers-storage/pkg/mount/mounter_linux_test.go

Purpose: validates Linux mount syscall sequencing and resulting mountinfo options.

Important APIs, types, and functions: `TestMount`, `ensureUnmount`, `validateMount`, `clean`, and `has`.

Control flow: root-only test creates a tmpfs source, then runs table-driven cases for bind, propagation modes, rw/ro, and remount data changes. After each mount, it reads mountinfo, compares expected ordinary options, optional propagation fields, and VFS options while allowing kernel-volunteered defaults.

State and persistence: temporarily mutates the current mount namespace and cleans up with `Unmount`.

Dependencies and integration points: depends on `fmt`, `os`, `strings`, and `testing`. It integrates `Mount`, `MakeShared`, `MakePrivate`, `GetMounts`, and Linux mountinfo parsing.

Risks and edge cases: root required. Shared/slave propagation cases depend on the source mount being made shared and then restored private. Kernel/default option variation is partially allowed by volunteered maps.

Test signals: strong coverage for Linux bind read-only remount mechanics, propagation remounts, remount data changes, and mountinfo validation.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/mount/mounter_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/mount/mounter_unsupported.go -->
# sources/cloud-native/containers-storage/pkg/mount/mounter_unsupported.go

Purpose: marks mount operations unsupported on platforms other than Linux and FreeBSD+cgo.

Important APIs, types, and functions: platform `mount`.

Control flow: immediately panics with `"Not implemented"`.

State and persistence: no state; no mount operation is attempted.

Dependencies and integration points: selected for `!linux && !(freebsd && cgo)`. High-level `Mount` and `ForceMount` will reach this implementation on unsupported platforms.

Risks and edge cases: runtime panic rather than returned error, so callers must platform-guard mount operations. This is unsuitable for graceful degradation unless wrapped.

Test signals: no direct tests; compile-time selection is the main signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/mount/mounter_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/mount/mountinfo.go -->
# sources/cloud-native/containers-storage/pkg/mount/mountinfo.go

Purpose: re-exports mountinfo parsing and mounted checks through the local `mount` package.

Important APIs, types, and functions: type alias `Info`, variable alias `Mounted`, and `GetMounts`.

Control flow: `GetMounts` delegates to `mountinfo.GetMounts(nil)`.

State and persistence: reads mount table information from the platform mountinfo implementation; no mutation.

Dependencies and integration points: depends on `github.com/moby/sys/mountinfo`. Used by high-level mount checks, recursive unmount, and tests.

Risks and edge cases: returned mount data reflects the current namespace and can change concurrently. Filter is nil, so all mounts are returned.

Test signals: `mount_unix_test.go` checks that `/` appears in mounts and that mounted targets are detected.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/mount/mountinfo.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/mount/mountinfo_linux.go -->
# sources/cloud-native/containers-storage/pkg/mount/mountinfo_linux.go

Purpose: reads mountinfo for an arbitrary Linux process ID.

Important APIs, types, and functions: `PidMountInfo(pid int) ([]*Info, error)`.

Control flow: opens `/proc/<pid>/mountinfo`, defers close, and parses it with `mountinfo.GetMountsFromReader`.

State and persistence: reads another process's mount namespace view as exposed by procfs; no mutation.

Dependencies and integration points: depends on `fmt`, `os`, and `github.com/moby/sys/mountinfo`. Useful for inspecting container or process mount namespaces.

Risks and edge cases: fails if procfs is unavailable, pid exits, or permissions prevent reading. It does not validate pid beyond path formatting.

Test signals: no direct requested tests; mountinfo parser coverage comes indirectly from current-process mount tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/mount/mountinfo_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/mount/sharedsubtree_linux.go -->
# sources/cloud-native/containers-storage/pkg/mount/sharedsubtree_linux.go

Purpose: exposes helpers to set Linux mount propagation modes on a mountpoint.

Important APIs, types, and functions: `MakeShared`, `MakeRShared`, `MakePrivate`, `MakeRPrivate`, `MakeSlave`, `MakeRSlave`, `MakeUnbindable`, `MakeRUnbindable`, and private `ensureMountedAs`.

Control flow: each public helper calls `ensureMountedAs` with the matching propagation flag. `ensureMountedAs` checks whether the path is mounted; if not, it bind-mounts the path onto itself, then applies the propagation remount.

State and persistence: mutates the current mount namespace by creating a self-bind mount when necessary and changing propagation attributes.

Dependencies and integration points: uses `Mounted` and platform `mount` from this package. It is Linux-only and feeds container mount propagation setup.

Risks and edge cases: requires privileges. Making an unmounted path into a self-bind mount changes mount topology and must be undone by callers. Propagation changes can affect child mount behavior broadly.

Test signals: `sharedsubtree_linux_test.go` verifies private, shared, slave, and unbindable propagation semantics using real bind mounts.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/mount/sharedsubtree_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/mount/sharedsubtree_linux_test.go -->
# sources/cloud-native/containers-storage/pkg/mount/sharedsubtree_linux_test.go

Purpose: integration-tests Linux shared-subtree propagation semantics.

Important APIs, types, and functions: `TestSubtreePrivate`, `TestSubtreeShared`, `TestSubtreeSharedSlave`, `TestSubtreeUnbindable`, and helper `createFile`.

Control flow: root-only tests create source/target/outside directories, set propagation modes with `MakePrivate`, `MakeShared`, `MakeSlave`, or `MakeUnbindable`, perform bind mounts into source or target subdirectories, and check whether files appear across propagation boundaries.

State and persistence: mutates the mount namespace with self-bind, bind, and propagation remounts; temporary directories and mounts are cleaned in defers.

Dependencies and integration points: depends on `errors`, `os`, `path`, `testing`, and `x/sys/unix`. It validates `sharedsubtree_linux.go`, `Mount`, and `Unmount` against kernel behavior.

Risks and edge cases: requires root and a mount namespace where propagation changes are permitted. Cleanup must unmount in the right order. Tests may be sensitive to environment defaults.

Test signals: strong semantic signals for no propagation under private, target-to-source propagation under shared, one-way source-to-slave propagation, and bind failure for unbindable mounts.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/mount/sharedsubtree_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/mount/unmount_unix.go -->
# sources/cloud-native/containers-storage/pkg/mount/unmount_unix.go

Purpose: implements Unix unmount with retry handling.

Important APIs, types, and functions: platform `unmount(target string, flags int) error`.

Control flow: tries `unix.Unmount` up to 50 times. On `EBUSY`, sleeps 50ms and retries. On `EINVAL` or nil, returns nil, treating not-mounted as success. Other errors break and are wrapped in `mountError`.

State and persistence: mutates the mount namespace by removing a mount. No package-level state.

Dependencies and integration points: depends on `time` and `golang.org/x/sys/unix`; called by `Unmount`, `ForceUnmount`, and recursive cleanup.

Risks and edge cases: `EINVAL` can also indicate invalid flags, but the code assumes flags are correct. Lazy detach semantics depend on the passed `mntDetach` constant. Worst-case retry takes about 2.5 seconds.

Test signals: exercised indirectly by Linux mount tests and shared-subtree tests during cleanup.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/mount/unmount_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/mount/unmount_unsupported.go -->
# sources/cloud-native/containers-storage/pkg/mount/unmount_unsupported.go

Purpose: marks unmount unsupported on Windows.

Important APIs, types, and functions: platform `unmount`.

Control flow: immediately panics with `"Not implemented"`.

State and persistence: no state or unmount action occurs.

Dependencies and integration points: selected for Windows builds. High-level `Unmount` reaches this implementation unless guarded.

Risks and edge cases: panic-based unsupported behavior requires callers to avoid mount APIs on Windows.

Test signals: no direct tests; compile-time selection is the main signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/mount/unmount_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/parsers/kernel/kernel.go -->
# sources/cloud-native/containers-storage/pkg/parsers/kernel/kernel.go

Purpose: defines cross-Unix kernel version representation, parsing, comparison, and minimum-version checks.

Important APIs, types, and functions: `VersionInfo`, `String`, `CompareKernelVersion`, `CheckKernelVersion`, and `ParseRelease`.

Control flow: `ParseRelease` uses `fmt.Sscanf` to parse kernel and major components plus a partial tail, then parses optional minor/flavor. `CompareKernelVersion` compares kernel, major, and minor numerically. `CheckKernelVersion` calls platform `GetKernelVersion`, logs warning on error, and returns true unless a successfully read version is below the requested threshold.

State and persistence: no persistence. State is returned as `VersionInfo`.

Dependencies and integration points: depends on `errors`, `fmt`, and `logrus`. Platform files provide `GetKernelVersion` for Unix variants.

Risks and edge cases: flavor is ignored by comparisons. `CheckKernelVersion` defaults to true if version lookup fails, favoring permissive behavior. Parser accepts versions without a third numeric component by setting minor zero.

Test signals: `kernel_unix_test.go` covers parse formats, invalid strings, and numeric comparisons.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/parsers/kernel/kernel.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/parsers/kernel/kernel_darwin.go -->
# sources/cloud-native/containers-storage/pkg/parsers/kernel/kernel_darwin.go

Purpose: implements Darwin kernel version retrieval.

Important APIs, types, and functions: `GetKernelVersion` and private `getRelease`.

Control flow: runs `system_profiler SPSoftwareDataType`, scans for `Kernel Version`, splits after the colon, parses the value with shellwords, expects `Darwin x.x.x`, and returns the version string to `ParseRelease`.

State and persistence: no persistence; reads current system profiler output.

Dependencies and integration points: depends on `fmt`, `os/exec`, `strings`, and `github.com/mattn/go-shellwords`. It plugs into common kernel parsing.

Risks and edge cases: external command can be slow, unavailable, localized, or produce unexpected formatting. Empty release returns through `ParseRelease` as an error.

Test signals: no Darwin-specific tests in the requested set; common parser tests cover release parsing after retrieval.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/parsers/kernel/kernel_darwin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/parsers/kernel/kernel_unix.go -->
# sources/cloud-native/containers-storage/pkg/parsers/kernel/kernel_unix.go

Purpose: implements kernel version retrieval for Unix platforms other than Darwin.

Important APIs, types, and functions: `GetKernelVersion`.

Control flow: calls `unix.Uname`, converts `uts.Release` to a Go string, and passes it to `ParseRelease`.

State and persistence: no persistence; reads current kernel release from uname.

Dependencies and integration points: depends on `golang.org/x/sys/unix` and common parser code. Selected for `unix && !darwin`.

Risks and edge cases: parsing can fail for unusual release strings. Uname errors are propagated.

Test signals: common Unix tests validate parser behavior; this function itself is not mocked in the requested tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/parsers/kernel/kernel_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/parsers/kernel/kernel_unix_test.go -->
# sources/cloud-native/containers-storage/pkg/parsers/kernel/kernel_unix_test.go

Purpose: tests kernel release parsing and version comparison on non-Windows builds.

Important APIs, types, and functions: `assertParseRelease`, `TestParseRelease`, `assertKernelVersion`, and `TestCompareKernelVersion`.

Control flow: parse tests feed representative kernel strings with flavors and missing minor components, then compare parsed results with expected `VersionInfo`. Invalid strings check exact error text. Comparison tests exercise equality and less/greater cases across kernel, major, and minor fields.

State and persistence: no state beyond test data.

Dependencies and integration points: depends on `fmt` and `testing`; validates `kernel.go` independently of actual host kernel.

Risks and edge cases: tests do not cover `CheckKernelVersion` or platform `GetKernelVersion`. Flavor comparison is only checked for parse preservation, not ordering.

Test signals: strong parser coverage for common Linux/Debian/Gentoo-style release forms and numeric ordering.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/parsers/kernel/kernel_unix_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/parsers/kernel/kernel_windows.go -->
# sources/cloud-native/containers-storage/pkg/parsers/kernel/kernel_windows.go

Purpose: implements Windows kernel/version information retrieval.

Important APIs, types, and functions: Windows-specific `VersionInfo`, `String`, and `GetKernelVersion`.

Control flow: opens the Windows registry key for current version, reads `BuildLabEx` into `kvi`, then calls `windows.GetVersion` to populate major, minor, and build fields.

State and persistence: reads registry and OS version state; no mutation.

Dependencies and integration points: depends on `fmt`, `unsafe`, and `golang.org/x/sys/windows`. This file replaces the Unix `VersionInfo` shape under Windows.

Risks and edge cases: comments note executable manifest requirements for accurate `GetVersion` output. Registry access can fail and returns a partially populated `"Unknown"` value with error.

Test signals: no Windows tests in the requested set; behavior depends on platform registry/API integration.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/parsers/kernel/kernel_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/parsers/operatingsystem/operatingsystem_linux.go -->
# sources/cloud-native/containers-storage/pkg/parsers/operatingsystem/operatingsystem_linux.go

Purpose: detects Linux operating system display name and whether PID 1 appears containerized.

Important APIs, types, and functions: package variables `proc1Cgroup`, `etcOsRelease`, `altOsRelease`; functions `GetOperatingSystem` and `IsContainerized`.

Control flow: `GetOperatingSystem` opens `/etc/os-release`, falls back to `/usr/lib/os-release`, scans for `PRETTY_NAME=`, parses with shellwords, and defaults to `"Linux"` if absent. `IsContainerized` reads `/proc/1/cgroup` and returns true when any non-empty cgroup path does not end in `/` or `init.scope`.

State and persistence: reads host/container files only. Test code can override package variables.

Dependencies and integration points: depends on `bufio`, `bytes`, `fmt`, `os`, `strings`, and `go-shellwords`. Used by environment reporting logic in containers-storage consumers.

Risks and edge cases: cgroup v2 and systemd layouts can evolve; heuristic may misclassify. PRETTY_NAME with spaces must be quoted. Scanner ignores read errors until after loop? It does not check `scanner.Err`, so read errors after scanning are not reported.

Test signals: Linux OS tests cover valid/invalid PRETTY_NAME, fallback file, and containerized/non-containerized cgroup layouts.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/parsers/operatingsystem/operatingsystem_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/parsers/operatingsystem/operatingsystem_solaris.go -->
# sources/cloud-native/containers-storage/pkg/parsers/operatingsystem/operatingsystem_solaris.go

Purpose: implements Solaris OS name and zone/container detection.

Important APIs, types, and functions: package variable `etcOsRelease`, `GetOperatingSystem`, and `IsContainerized`.

Control flow: `GetOperatingSystem` reads `/etc/release`, returns the first trimmed line, or errors if no newline is found. `IsContainerized` calls `getzoneid` and treats any nonzero zone id as containerized.

State and persistence: reads OS release file and current zone id; no mutation.

Dependencies and integration points: depends on cgo `zone.h`, `bytes`, `errors`, and `os`. Selected for `solaris && cgo`.

Risks and edge cases: cgo required. A release file without newline returns an error even if content exists. Containerization is Solaris-zone-specific.

Test signals: no Solaris tests in the requested set.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/parsers/operatingsystem/operatingsystem_solaris.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/parsers/operatingsystem/operatingsystem_unix.go -->
# sources/cloud-native/containers-storage/pkg/parsers/operatingsystem/operatingsystem_unix.go

Purpose: implements basic OS name lookup for FreeBSD and Darwin.

Important APIs, types, and functions: `GetOperatingSystem` and `IsContainerized`.

Control flow: `GetOperatingSystem` runs `uname -s` and returns its raw output. `IsContainerized` always returns false with an explanatory error because jail/container detection is not implemented.

State and persistence: no persistence; reads system command output.

Dependencies and integration points: depends on `errors` and `os/exec`; selected for FreeBSD or Darwin builds.

Risks and edge cases: returned OS name includes the trailing newline. Container detection callers must handle the non-nil error.

Test signals: no FreeBSD/Darwin-specific tests in requested files.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/parsers/operatingsystem/operatingsystem_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/parsers/operatingsystem/operatingsystem_unix_test.go -->
# sources/cloud-native/containers-storage/pkg/parsers/operatingsystem/operatingsystem_unix_test.go

Purpose: tests Linux operating system name parsing, os-release fallback, and container detection heuristics.

Important APIs, types, and functions: `TestGetOperatingSystem`, `TestIsContainerized`, and `TestOsReleaseFallback`.

Control flow: tests override `etcOsRelease`, `altOsRelease`, and `proc1Cgroup` to temporary files. They write invalid and valid os-release content, verify exact outputs/errors, and exercise cgroup layouts for host, systemd init.scope host, and Docker-like container paths.

State and persistence: writes temporary files under `os.TempDir` and restores package variables in defers.

Dependencies and integration points: depends on `os`, `filepath`, and `testing`. It validates `operatingsystem_linux.go`.

Risks and edge cases: using shared `os.TempDir` filenames can conflict if tests run in parallel, though these tests do not call `t.Parallel`. Cleanup defers include `os.Remove(dir)` on a system temp directory in fallback test, which is risky but likely harmless if the directory is not empty.

Test signals: strong parser signals for quoting requirements, duplicate PRETTY_NAME where later wins, default Linux fallback, alt release fallback, and cgroup container heuristics.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/parsers/operatingsystem/operatingsystem_unix_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/parsers/operatingsystem/operatingsystem_windows.go -->
# sources/cloud-native/containers-storage/pkg/parsers/operatingsystem/operatingsystem_windows.go

Purpose: retrieves the Windows product name and reports containerization unsupported/false.

Important APIs, types, and functions: `GetOperatingSystem` and `IsContainerized`.

Control flow: opens the Windows current-version registry key, reads `ProductName` into a UTF-16 buffer, converts it to string, and returns `"Unknown Operating System"` with an error on failures. `IsContainerized` returns false, nil.

State and persistence: reads registry state only.

Dependencies and integration points: depends on `unsafe` and `golang.org/x/sys/windows`; selected on Windows.

Risks and edge cases: registry access errors propagate with default string. Buffer size is fixed at 1024 UTF-16 code units. No Windows container detection is attempted.

Test signals: no Windows-specific tests in the requested set.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/parsers/operatingsystem/operatingsystem_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/parsers/parsers.go -->
# sources/cloud-native/containers-storage/pkg/parsers/parsers.go

Purpose: provides generic string parsers for key/value options and unsigned integer/range lists used by cgroup-style files.

Important APIs, types, and functions: `ParseKeyValueOpt` and `ParseUintList`.

Control flow: `ParseKeyValueOpt` splits on the first `=`, trims spaces around key and value, and errors if no separator exists. `ParseUintList` splits comma-separated entries, accepts single integers and `min-max` ranges, validates numeric conversion and range order, and marks every included integer in a map.

State and persistence: no state or persistence; functions return parsed values.

Dependencies and integration points: depends on `fmt`, `strconv`, and `strings`. Useful for cgroup cpuset/memory parser call sites.

Risks and edge cases: despite the name, `ParseUintList` uses `strconv.Atoi` and therefore accepts negative single integers unless rejected by format in tests; `-1` fails because it is parsed as a malformed range due to `strings.Cut`. Large ranges can allocate huge maps and loop extensively.

Test signals: `parsers_test.go` covers trimming, values containing `=`, empty input, duplicate/overlap ranges, leading zeros, reverse ranges, malformed separators, and invalid tokens.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/parsers/parsers.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/parsers/parsers_test.go -->
# sources/cloud-native/containers-storage/pkg/parsers/parsers_test.go

Purpose: tests generic parsers from `parsers.go`.

Important APIs, types, and functions: `TestParseKeyValueOpt` and `TestParseUintList`.

Control flow: key/value tests check invalid missing-separator inputs and valid trimming/value-preserving cases. uint-list tests compare returned maps for singles, ranges, duplicates, leading zeros, and order variations, then assert malformed strings fail.

State and persistence: no state or persistence.

Dependencies and integration points: depends on `reflect` and `testing`. It protects parsing behavior expected by cgroup-style callers.

Risks and edge cases: map comparison ignores ordering, as intended. Tests do not include extremely large ranges or integer overflow.

Test signals: confirms accepted grammar and exact error behavior for common invalid forms.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/parsers/parsers_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/pools/pools.go -->
# sources/cloud-native/containers-storage/pkg/pools/pools.go

Purpose: centralizes reusable `bufio.Reader` and `bufio.Writer` pools to reduce allocations.

Important APIs, types, and functions: globals `BufioReader32KPool`, `BufioWriter32KPool`; `BufioReaderPool`, `BufioWriterPool`; `Get`, `Put`, `Copy`, `NewReadCloserWrapper`, and `NewWriteCloserWrapper`.

Control flow: `init` creates 32K reader and writer pools. `Get` obtains a pooled buffer and resets it to a new reader/writer. `Put` resets to nil and returns to the pool. `Copy` uses the reader pool with `io.Copy`. Wrapper constructors return closers that flush/close underlying objects where applicable and return buffers to the pool.

State and persistence: in-memory `sync.Pool` state only. No persistence.

Dependencies and integration points: depends on `bufio`, `io`, `sync`, and `ioutils`. Used by performance-sensitive stream paths needing pooled buffered I/O.

Risks and edge cases: callers must not use buffers after `Put`; tests demonstrate such use can panic. `NewReadCloserWrapper` wraps `r`, not the provided `buf`, so passing a separate `buf` requires callers to ensure reads go through the intended object. Close wrappers ignore underlying close errors in the reader case.

Test signals: `pools_test.go` covers get/put behavior, wrapper close behavior, writer flushing, and after-put reset consequences.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/pools/pools.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/pools/pools_test.go -->
# sources/cloud-native/containers-storage/pkg/pools/pools_test.go

Purpose: tests pooled buffered reader/writer helpers.

Important APIs, types, and functions: tests for reader pool get/put, read closer wrapper, writer pool get/put, and write closer wrapper; helper types `simpleReaderCloser` and `simpleWriterCloser`.

Control flow: tests obtain buffers, perform reads/writes, return buffers, and verify reset behavior. Writer tests flush buffers and intentionally expect a panic when flushing a writer after it was reset to nil by `Put`.

State and persistence: no persistence. State includes pooled buffer internals, backing buffers, and closed flags.

Dependencies and integration points: depends on `bufio`, `bytes`, `io`, `strings`, and `testing`. It validates pool behavior for `ioutils` wrapper integration.

Risks and edge cases: one test reads from a wrapper after closing it, relying on the wrapper not preventing future reads. Tests do not cover concurrent pool use beyond `sync.Pool` basics.

Test signals: confirms allocation path, reset semantics, wrapper close/flush/close actions, and misuse-after-put panic behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/pools/pools_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/promise/promise.go -->
# sources/cloud-native/containers-storage/pkg/promise/promise.go

Purpose: provides a minimal async helper that runs an error-returning function in a goroutine.

Important APIs, types, and functions: `Go(f func() error) chan error`.

Control flow: creates a buffered error channel of size one, starts a goroutine, sends `f()` result, and returns the channel immediately.

State and persistence: no persistence. The returned channel is the only synchronization state.

Dependencies and integration points: no imports. Used where callers want to launch work and later wait for one error result.

Risks and edge cases: no panic recovery, cancellation, context, or channel close. The channel buffer prevents the goroutine from blocking if caller never reads one result, but further protocol is absent.

Test signals: `promise_test.go` verifies both error and nil paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/promise/promise.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/promise/promise_test.go -->
# sources/cloud-native/containers-storage/pkg/promise/promise_test.go

Purpose: tests the minimal promise helper.

Important APIs, types, and functions: `TestGo`, `functionWithError`, and `functionWithNoError`.

Control flow: calls `Go` with an error-returning function, reads the channel, checks error text, then repeats with a nil-returning function and checks nil.

State and persistence: no persistence. State is a buffered channel result.

Dependencies and integration points: depends on `errors`, `testing`, and `testify/require`.

Risks and edge cases: tests do not cover panic behavior, unread channels, or timing.

Test signals: verifies that `Go` executes the function asynchronously and returns the exact error value through the channel.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/promise/promise_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/reexec/command_freebsd.go -->
# sources/cloud-native/containers-storage/pkg/reexec/command_freebsd.go

Purpose: implements FreeBSD self-reexec command construction.

Important APIs, types, and functions: `Self`, `Command`, and `CommandContext`.

Control flow: `Self` uses `unix.SysctlArgs("kern.proc.pathname", -1)` and falls back to `os.Args[0]`. `Command` and `CommandContext` build exec commands targeting `Self()` and replace `cmd.Args` with the requested reexec args.

State and persistence: no persistence. It depends on current process path and command args.

Dependencies and integration points: depends on `context`, `os`, `os/exec`, and `x/sys/unix`. It is part of the `reexec` mechanism used by tests and subprocess isolation.

Risks and edge cases: unlike other platforms here, this file does not call `panicIfNotInitialized`, so FreeBSD behavior differs. Fallback to `os.Args[0]` may be relative or deleted.

Test signals: generic reexec tests exercise command behavior where platform support permits, but FreeBSD path lookup is not specifically tested.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/reexec/command_freebsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/reexec/command_linux.go -->
# sources/cloud-native/containers-storage/pkg/reexec/command_linux.go

Purpose: implements Linux self-reexec command construction using `/proc/self/exe`.

Important APIs, types, and functions: `Self`, `Command`, and `CommandContext`.

Control flow: `Self` returns `/proc/self/exe`. Command constructors first require `Init` to have been called, create an `exec.Cmd` or context-aware command for `/proc/self/exe`, and set `cmd.Args` to the requested child argv.

State and persistence: no persistence. Uses the kernel's live executable reference, so it remains valid if the on-disk binary is replaced.

Dependencies and integration points: depends on `context` and `os/exec`. Used by lockfile tests and any package that registers reexec initializers.

Risks and edge cases: panics if `reexec.Init` was not called in main. `/proc` must be mounted and accessible.

Test signals: `reexec_test.go` covers `Command` and `CommandContext` on supported platforms.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/reexec/command_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/reexec/command_unix.go -->
# sources/cloud-native/containers-storage/pkg/reexec/command_unix.go

Purpose: implements self-reexec command construction for Solaris and Darwin.

Important APIs, types, and functions: `Self`, `Command`, and `CommandContext`.

Control flow: `Self` delegates to `naiveSelf`, which resolves `os.Args[0]`. Command constructors require initialization, create commands for `Self()`, and set `cmd.Args` to the child argv.

State and persistence: no persistence. Relies on the current executable path being resolvable and still usable.

Dependencies and integration points: depends on `context` and `os/exec`; uses common `reexec.go` helpers.

Risks and edge cases: unlike Linux, a deleted or replaced on-disk binary can break reexec. Initialization panic protects callers from missing `Init`.

Test signals: generic reexec tests cover behavior on supported platforms; `naiveSelf` has direct test coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/reexec/command_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/reexec/command_unsupported.go -->
# sources/cloud-native/containers-storage/pkg/reexec/command_unsupported.go

Purpose: provides unsupported stubs for reexec command construction.

Important APIs, types, and functions: `Command` and `CommandContext`.

Control flow: both call `panicIfNotInitialized` and then return nil. If initialized, the nil return indicates unsupported operation without an explicit panic.

State and persistence: no state or persistence.

Dependencies and integration points: depends on `context` and `os/exec`; selected outside Linux, Windows, FreeBSD, Solaris, and Darwin.

Risks and edge cases: returning nil after successful initialization can lead to nil pointer panics in callers expecting a command. Callers should platform-guard reexec usage.

Test signals: no unsupported-platform tests in the requested set.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/reexec/command_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/reexec/command_windows.go -->
# sources/cloud-native/containers-storage/pkg/reexec/command_windows.go

Purpose: implements Windows self-reexec command construction.

Important APIs, types, and functions: `Self`, `Command`, and `CommandContext`.

Control flow: `Self` uses `naiveSelf`. Command constructors require `Init`, create commands for `Self()`, and set `cmd.Args` to the requested reexec argv.

State and persistence: no persistence. Depends on the current executable path.

Dependencies and integration points: depends on `context` and `os/exec`; uses common registration/init logic.

Risks and edge cases: deleted or moved binaries can break reexec. The comment for `CommandContext` repeats "Command", but behavior is context-aware. Initialization must run before use.

Test signals: generic reexec tests exercise command construction and context cancellation where platform support permits.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/reexec/command_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/reexec/reexec.go -->
# sources/cloud-native/containers-storage/pkg/reexec/reexec.go

Purpose: provides registration and dispatch for reexecuting the current binary into named subroutines.

Important APIs, types, and functions: `Register`, `Init`, `panicIfNotInitialized`, `naiveSelf`, and globals `registeredInitializers` and `initWasCalled`.

Control flow: packages register initializers by name. `Init` marks initialization called, checks whether `os.Args[0]` matches a registered name, runs the initializer if found, and returns true to tell main to exit. `panicIfNotInitialized` enforces that command constructors are only used after `Init`. `naiveSelf` resolves `os.Args[0]` through `LookPath` or absolute path conversion.

State and persistence: global in-memory registry and initialization flag. No persistence.

Dependencies and integration points: depends on `fmt`, `os`, `os/exec`, and `filepath`. Used by lockfile tests and any code needing subprocess execution of internal functions.

Risks and edge cases: duplicate registration panics. Matching on `os.Args[0]` means command constructors must set `cmd.Args` exactly to registered names. Registry is not concurrency-protected.

Test signals: `reexec_test.go` covers duplicate registration, child command dispatch, context cancellation, and `naiveSelf` resolution.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/reexec/reexec.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/reexec/reexec_test.go -->
# sources/cloud-native/containers-storage/pkg/reexec/reexec_test.go

Purpose: tests reexec registration, child dispatch, context cancellation, and self-path resolution.

Important APIs, types, and functions: init-time registrations for `reexec` and `sleep`, `TestRegister`, `TestCommand`, `TestCommandContext`, and `TestNaiveSelf`.

Control flow: init registers child functions and calls `Init`. Tests assert duplicate registration panics, run a child that panics and expect exit status 2, run a sleeping child with deadline cancellation and check stdout, and run `naiveSelf` through a subprocess plus `LookPath` resolution.

State and persistence: mutates global reexec registry and `os.Args[0]` in the naive-self test. No persistence.

Dependencies and integration points: depends on `bytes`, `context`, `fmt`, `os`, `os/exec`, `testing`, `time`, and `testify`. It validates command files for the current platform.

Risks and edge cases: init-time `Init` changes package-global state for all tests. The deadline test depends on scheduler/process timing but uses a generous 5-second deadline.

Test signals: confirms registration uniqueness, argv-based dispatch, context-driven process termination, stdout propagation before cancellation, and executable path resolution.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/reexec/reexec_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/regexp/regexp.go -->
# sources/cloud-native/containers-storage/pkg/regexp/regexp.go

Purpose: wraps Go regular expressions so global regex variables can be lazily compiled, reducing startup cost unless a build tag requests precompilation.

Important APIs, types, and functions: `Regexp`, `Delayed`, private `regexpStruct`, `compile`, wrapper methods for most `regexp.Regexp` operations, and `noCopy`.

Control flow: `Delayed` stores the pattern and optionally compiles immediately when `precompile` is true. Every method calls `compile`, which uses `sync.Once` to compile lazily when not precompiled, then delegates to the embedded `regexp.Regexp`.

State and persistence: in-memory compiled regex cache per `Regexp`. No persistence.

Dependencies and integration points: depends on `io`, stdlib `regexp`, and `sync`. Used by string/id validation and any package wanting delayed global regexes.

Risks and edge cases: invalid regex patterns panic at first use, not declaration time, unless precompiled. `Longest` mutates regex matching behavior after compile. Copying after use is discouraged through `noCopy` vet signaling but not runtime-enforced.

Test signals: `regexp_test.go` covers interface compatibility, `MatchString`, and `FindStringSubmatch`.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/regexp/regexp.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/regexp/regexp_dontprecompile.go -->
# sources/cloud-native/containers-storage/pkg/regexp/regexp_dontprecompile.go

Purpose: default build configuration for lazy regex compilation.

Important APIs, types, and functions: constant `precompile = false`.

Control flow: no runtime flow; `regexp.go` reads this constant in `Delayed` and `compile`.

State and persistence: no state. It changes whether regex state is created at declaration or first use.

Dependencies and integration points: selected when build tag `regexp_precompile` is absent. It is the normal startup-optimized path.

Risks and edge cases: invalid regex patterns panic later at first method call, which can defer failures into runtime paths.

Test signals: normal tests run under this behavior unless the build tag is set.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/regexp/regexp_dontprecompile.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/regexp/regexp_precompile.go -->
# sources/cloud-native/containers-storage/pkg/regexp/regexp_precompile.go

Purpose: build-tag configuration that forces regex compilation during `Delayed`.

Important APIs, types, and functions: constant `precompile = true`.

Control flow: no runtime flow here; `regexp.go` uses the constant to compile in `Delayed` and skip lazy compile.

State and persistence: no persistence. Compiled regex state is created eagerly.

Dependencies and integration points: selected with build tag `regexp_precompile`. Useful when startup failures for invalid regexes are preferred over lazy runtime panics.

Risks and edge cases: increases startup work for global regex declarations but catches invalid patterns earlier.

Test signals: no explicit tagged test in the requested files; the same `regexp_test.go` should pass under either tag.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/regexp/regexp_precompile.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/regexp/regexp_test.go -->
# sources/cloud-native/containers-storage/pkg/regexp/regexp_test.go

Purpose: tests the delayed regexp wrapper.

Important APIs, types, and functions: interface `partOfRegexp`, compile-time assignment `var _ partOfRegexp = &Regexp{}`, `TestMatchString`, and `TestFindStringSubmatch`.

Control flow: tests create delayed regexes, call matching/submatch methods, and assert expected match and non-match outcomes.

State and persistence: no persistence. Tests cause lazy compilation under default builds.

Dependencies and integration points: depends on `testing`. It validates enough wrapper surface to catch broken embedding/delegation for common methods.

Risks and edge cases: only a tiny subset of the delegated methods is tested. Invalid pattern panic behavior and precompile build tag behavior are not explicitly tested.

Test signals: confirms lazy wrapper implements expected methods and delegates match/submatch operations correctly.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/regexp/regexp_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/stringid/stringid.go -->
# sources/cloud-native/containers-storage/pkg/stringid/stringid.go

Purpose: generates, truncates, and validates 64-character hex identifiers used for images and storage objects.

Important APIs, types, and functions: `IsShortID`, `TruncateID`, `GenerateRandomID`, `GenerateNonCryptoID`, `ValidateID`, private `generateID`, `readerFunc`, regex globals, and private pseudo-random generator state.

Control flow: `generateID` reads 32 bytes from a reader, hex-encodes them, rejects IDs whose 12-character truncation parses as a decimal integer, and retries. Crypto generation uses `crypto/rand.Reader`; non-crypto generation uses a locked private `math/rand.Rand` seeded with crypto randomness or time. `TruncateID` strips a prefix before `:` and returns at most 12 characters.

State and persistence: no persistence. Global `rng` and `rngLock` maintain non-crypto random sequence state.

Dependencies and integration points: depends on crypto, encoding, math/rand, strings, sync, time, and delayed regex wrapper. Used by storage object ID generation and validation.

Risks and edge cases: `GenerateNonCryptoID` is not cryptographically secure despite crypto seeding. `generateID` panics on reader failure. Validation only accepts lowercase 64-hex strings. Short ID collisions remain possible.

Test signals: `stringid_test.go` covers generated lengths, truncation of raw and `sha256:` IDs, empty/short truncation, and short-ID validation negatives.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/stringid/stringid.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/stringid/stringid_test.go -->
# sources/cloud-native/containers-storage/pkg/stringid/stringid_test.go

Purpose: tests identifier generation, truncation, and short-ID recognition.

Important APIs, types, and functions: `TestGenerateRandomID`, `TestGenerateNonCryptoID`, `TestShortenId`, `TestShortenSha256Id`, `TestShortenIdEmpty`, `TestShortenIdInvalid`, `TestIsShortIDNonHex`, and `TestIsShortIDNotCorrectSize`.

Control flow: tests call generators and check 64-character length, call `TruncateID` with full, prefixed, empty, and already-short strings, and verify invalid short-ID cases.

State and persistence: no persistence. Generator tests consume randomness and the global non-crypto RNG.

Dependencies and integration points: depends on `strings` and `testing`. It validates behavior for storage ID display and validation helpers.

Risks and edge cases: tests do not validate `ValidateID`, all-numeric truncated rejection, uniqueness, uppercase rejection, or collision behavior.

Test signals: confirms core display truncation and basic generated ID shape.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/stringid/stringid_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/stringutils/stringutils.go -->
# sources/cloud-native/containers-storage/pkg/stringutils/stringutils.go

Purpose: provides string generation, truncation, case-insensitive slice helpers, and shell argument quoting.

Important APIs, types, and functions: `GenerateRandomAlphaOnlyString`, `GenerateRandomASCIIString`, `Ellipsis`, `Truncate`, `InSlice`, `RemoveFromSlice`, private `quote`, and `ShellQuoteArguments`.

Control flow: random generators fill byte slices from allowed character strings using `math/rand/v2`. `Ellipsis` and `Truncate` operate on runes to preserve Unicode code points. Slice helpers use `strings.EqualFold`. Shell quoting leaves simple strings bare and single-quotes complex strings, escaping embedded single quotes with the standard close-escape-open sequence.

State and persistence: no persistence. Random output depends on package-level `math/rand/v2` source.

Dependencies and integration points: depends on `bytes`, `math/rand/v2`, and `strings`. Used by tests and callers needing display truncation or shell-safe command strings.

Risks and edge cases: random generators are not crypto-secure. Rune truncation can split grapheme clusters even though it preserves code points. Shell quoting targets POSIX shell style, not Windows cmd/PowerShell.

Test signals: `stringutils_test.go` checks lengths, rough uniqueness, ASCII-only output, Unicode-safe truncation, case-insensitive membership, and shell quoting.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/stringutils/stringutils.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/stringutils/stringutils_test.go -->
# sources/cloud-native/containers-storage/pkg/stringutils/stringutils_test.go

Purpose: tests random string helpers, Unicode-aware truncation, case-insensitive membership, and shell quoting.

Important APIs, types, and functions: helper functions `testLengthHelper`, `testUniquenessHelper`, `isASCII`, tests for alpha/ASCII generation, `TestEllipsis`, `TestTruncate`, `TestInSlice`, `TestShellQuoteArgumentsEmpty`, and `TestShellQuoteArguments`.

Control flow: generator tests verify length and no repeats over 25 generated 64-byte strings. Truncation tests use a string containing a multi-byte rune. Shell quote tests compare exact POSIX quoting output.

State and persistence: no persistence. Tests consume randomness and in-memory strings.

Dependencies and integration points: depends on `testing`. It validates public helpers in `stringutils.go`.

Risks and edge cases: uniqueness tests are probabilistic. Test strings include Unicode, which is useful for rune behavior but does not cover combining marks. Shell quoting tests cover a representative but not exhaustive set of metacharacters.

Test signals: confirms ASCII character set, length contracts, common truncation behavior, case-insensitive lookup, and quote escaping of embedded single quotes.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/stringutils/stringutils_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/chmod.go -->
# sources/cloud-native/containers-storage/pkg/system/chmod.go

Purpose: wraps `os.Chmod` with retry-on-interrupted-system-call behavior.

Important APIs, types, and functions: `Chmod(name string, mode os.FileMode) error`.

Control flow: calls `os.Chmod`; while the returned error matches `syscall.EINTR`, retries. Returns the final error.

State and persistence: mutates file mode on disk if successful. No package-level state.

Dependencies and integration points: depends on `errors`, `os`, and `syscall`. Used by filesystem code that wants robust chmod behavior around signals.

Risks and edge cases: retries indefinitely if `EINTR` repeats forever. Other transient errors are not retried. `errors.Is` is used for wrapped EINTR matching.

Test signals: no direct test in requested files.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/chmod.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/chtimes.go -->
# sources/cloud-native/containers-storage/pkg/system/chtimes.go

Purpose: safely changes file access and modification times while clamping values outside supported Unix time bounds.

Important APIs, types, and functions: `Chtimes(name string, atime time.Time, mtime time.Time) error`.

Control flow: computes Unix epoch and platform `maxTime`; if atime or mtime is before epoch or after max, replaces it with epoch. Calls `os.Chtimes`, then invokes platform `setCTime` to adjust create time where needed.

State and persistence: mutates filesystem timestamps. No package-level state beyond `maxTime` initialized in `init.go`.

Dependencies and integration points: depends on `os` and `time`; platform-specific `setCTime` files handle Unix no-op and Windows creation time.

Risks and edge cases: out-of-range times are silently coerced to epoch. On Unix, ctime cannot be directly set and changes as a side effect. Nanosecond precision depends on filesystem/platform.

Test signals: `chtimes_test.go`, Linux atime test, and Windows atime/create-time tests cover boundary clamping and valid time setting.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/chtimes.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/chtimes_linux_test.go -->
# sources/cloud-native/containers-storage/pkg/system/chtimes_linux_test.go

Purpose: validates Linux access-time behavior for `Chtimes`.

Important APIs, types, and functions: helper `atime` and `TestChtimesLinux`.

Control flow: creates a temp file, sets atime/mtime to epoch, before-epoch, after-epoch, and max-time combinations, then stats the file and compares Linux `Atim`.

State and persistence: mutates timestamps on a temporary file.

Dependencies and integration points: depends on `os`, `syscall`, `testing`, and `time`; uses shared `prepareTempFile` from `chtimes_test.go`.

Risks and edge cases: filesystem timestamp precision may require truncation for max-time checks. It is Linux-only and does not test ctime directly.

Test signals: confirms atime clamping to epoch for invalid values and correct atime for valid/max values on Linux.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/chtimes_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/chtimes_test.go -->
# sources/cloud-native/containers-storage/pkg/system/chtimes_test.go

Purpose: cross-platform tests for modification-time behavior of `Chtimes`.

Important APIs, types, and functions: `prepareTempFile` and `TestChtimes`.

Control flow: creates a temp file, calls `Chtimes` with epoch, before-epoch, after-epoch, and max-time combinations, and compares `os.FileInfo.ModTime`.

State and persistence: mutates temporary file timestamps.

Dependencies and integration points: depends on `os`, `filepath`, `testing`, and `time`; validates `chtimes.go` and platform `maxTime`.

Risks and edge cases: only mtime is checked because atime is OS-dependent. Max-time comparison truncates to seconds.

Test signals: confirms invalid atime/mtime clamping and valid mtime setting across platforms.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/chtimes_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/chtimes_unix.go -->
# sources/cloud-native/containers-storage/pkg/system/chtimes_unix.go

Purpose: provides Unix `setCTime` implementation for `Chtimes`.

Important APIs, types, and functions: `setCTime(path string, ctime time.Time) error`.

Control flow: returns nil without action because Unix ctime is kernel-maintained and changes as a side effect of metadata updates.

State and persistence: no direct mutation beyond the preceding `os.Chtimes` call in common code.

Dependencies and integration points: depends on `time`; selected for non-Windows builds.

Risks and edge cases: callers cannot set creation time or ctime on Unix through this API. The comment uses "create time" loosely, but Unix ctime is change time.

Test signals: common `Chtimes` tests run through this no-op on Unix.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/chtimes_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/chtimes_windows.go -->
# sources/cloud-native/containers-storage/pkg/system/chtimes_windows.go

Purpose: implements Windows creation-time setting after `os.Chtimes`.

Important APIs, types, and functions: `setCTime(path string, ctime time.Time) error`.

Control flow: converts the requested time to Windows timespec/filetime, opens the path with `FILE_WRITE_ATTRIBUTES` and backup semantics, defers handle close, and calls `windows.SetFileTime` with the creation time pointer.

State and persistence: mutates Windows file creation time metadata.

Dependencies and integration points: depends on `time` and `golang.org/x/sys/windows`; selected on Windows and called by common `Chtimes`.

Risks and edge cases: requires permission to write file attributes. Path conversion can fail. Directories need backup semantics, which are included.

Test signals: `chtimes_windows_test.go` validates access-time behavior under Windows; creation-time setting is not explicitly asserted in requested tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/chtimes_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/chtimes_windows_test.go -->
# sources/cloud-native/containers-storage/pkg/system/chtimes_windows_test.go

Purpose: validates Windows access-time behavior for `Chtimes`.

Important APIs, types, and functions: `TestChtimesWindows`.

Control flow: creates a temp file, calls `Chtimes` with epoch, before-epoch, after-epoch, and max-time combinations, then inspects `syscall.Win32FileAttributeData.LastAccessTime`.

State and persistence: mutates timestamps on a temporary file.

Dependencies and integration points: depends on `os`, `syscall`, `testing`, and `time`; uses common test helper and Windows stat structures.

Risks and edge cases: test calls `Chtimes` without checking returned errors, so failures may surface only through timestamp mismatch. It checks atime but not create time despite Windows-specific `setCTime`.

Test signals: confirms Windows atime clamping and valid/max value behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/chtimes_windows_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/errors.go -->
# sources/cloud-native/containers-storage/pkg/system/errors.go

Purpose: defines a shared unsupported-platform error for system helpers.

Important APIs, types, and functions: `ErrNotSupportedPlatform`.

Control flow: none beyond package variable initialization.

State and persistence: no persistence.

Dependencies and integration points: depends on `errors`. Used by unsupported extattr and meminfo implementations.

Risks and edge cases: callers should compare with `errors.Is` only if wrapping is added elsewhere; this file exposes a sentinel error.

Test signals: no direct tests in requested files.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/errors.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/exitcode.go -->
# sources/cloud-native/containers-storage/pkg/system/exitcode.go

Purpose: extracts process exit codes from `exec.ExitError` values.

Important APIs, types, and functions: `GetExitCode` and `ProcessExitCode`.

Control flow: `GetExitCode` type-asserts to `*exec.ExitError`, then to `syscall.WaitStatus`, and returns `ExitStatus`; otherwise returns error. `ProcessExitCode` returns zero for nil error, extracted code for recognized exit errors, and 127 when extraction fails.

State and persistence: no state or persistence.

Dependencies and integration points: depends on `fmt`, `os/exec`, and `syscall`. Used by command-running paths that need shell-like exit code handling.

Risks and edge cases: signal termination and non-Unix wait states may not map cleanly. Non-`ExitError` failures collapse to 127 in `ProcessExitCode`.

Test signals: no direct tests in requested files.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/exitcode.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/extattr_freebsd.go -->
# sources/cloud-native/containers-storage/pkg/system/extattr_freebsd.go

Purpose: implements FreeBSD extended attribute operations on symlink paths themselves.

Important APIs, types, and functions: namespace constants, `ExtattrGetLink`, `ExtattrSetLink`, and `ExtattrListLink`.

Control flow: get/list first call the FreeBSD syscall with nil buffer to get size, then allocate and call again. Missing attributes return nil, nil. Set ensures empty data is non-nil and passes the data pointer. List decodes FreeBSD's length-prefixed attribute names.

State and persistence: reads and writes filesystem extended attributes.

Dependencies and integration points: depends on `os`, `unsafe`, and `x/sys/unix`; selected on FreeBSD. Used by metadata/xattr preservation paths.

Risks and edge cases: `ExtattrSetLink` indexes `data[0]` even after setting empty data to `[]byte{}`, which is still length zero and would panic for empty input. Attribute list parsing silently stops on malformed length overrun.

Test signals: no FreeBSD extattr tests in requested files.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/extattr_freebsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/extattr_unsupported.go -->
# sources/cloud-native/containers-storage/pkg/system/extattr_unsupported.go

Purpose: provides unsupported stubs for FreeBSD-style extattr functions on non-FreeBSD platforms.

Important APIs, types, and functions: zero namespace constants, `ExtattrGetLink`, `ExtattrSetLink`, and `ExtattrListLink`.

Control flow: each function immediately returns `ErrNotSupportedPlatform`.

State and persistence: no filesystem mutation or read occurs.

Dependencies and integration points: selected for `!freebsd`; uses the shared unsupported sentinel. This keeps cross-platform callers compiling.

Risks and edge cases: namespace constants are zero and should not be used for real extattr work on unsupported platforms. Callers must handle unsupported errors.

Test signals: no direct tests in requested files.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/extattr_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/init.go -->
# sources/cloud-native/containers-storage/pkg/system/init.go

Purpose: initializes the platform maximum time supported by `Chtimes`.

Important APIs, types, and functions: package variable `maxTime` and `init`.

Control flow: checks the size of `syscall.Timespec{}.Nsec`; if 64-bit, sets `maxTime` to the maximum int64 nanosecond time, otherwise to the maximum 32-bit Unix seconds time.

State and persistence: initializes package-global in-memory state. No persistence.

Dependencies and integration points: depends on `syscall`, `time`, and `unsafe`. `chtimes.go` uses `maxTime` to clamp timestamps.

Risks and edge cases: heuristic is based on `Timespec.Nsec` size, which is a proxy for supported time range. Filesystem-specific timestamp limits may be narrower.

Test signals: `Chtimes` tests use `maxTime` and verify it can be set/truncated on supported filesystems.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/init.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/init_windows.go -->
# sources/cloud-native/containers-storage/pkg/system/init_windows.go

Purpose: initializes Windows LCOW support flag from the environment.

Important APIs, types, and functions: package variable `lcowSupported` and `init`.

Control flow: default is false; init sets true when environment variable `LCOW_SUPPORTED` is non-empty.

State and persistence: in-memory package-global state derived from process environment at init time.

Dependencies and integration points: depends on `os`; used by `lcow_windows.go`.

Risks and edge cases: environment is read only once at package initialization. Comment notes this was a development-era feature gate and may not reflect modern Windows capability detection.

Test signals: no direct Windows LCOW tests in requested files.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/init_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/lchflags_bsd.go -->
# sources/cloud-native/containers-storage/pkg/system/lchflags_bsd.go

Purpose: exposes FreeBSD file flag constants and `lchflags` syscall wrapper.

Important APIs, types, and functions: `UF_*` and `SF_*` constants plus `Lchflags`.

Control flow: converts path to a C-style byte pointer, invokes `SYS_LCHFLAGS` with the flag value, and returns syscall errno if nonzero.

State and persistence: mutates filesystem flags on a path without following symlinks.

Dependencies and integration points: depends on `unsafe` and `x/sys/unix`; selected on FreeBSD. Used by archive/metadata restoration paths needing BSD flags.

Risks and edge cases: requires permissions for system flags. Only FreeBSD build tag is present; other BSDs may need different support. Path conversion errors are returned.

Test signals: no direct tests in requested files.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/lchflags_bsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/lchown.go -->
# sources/cloud-native/containers-storage/pkg/system/lchown.go

Purpose: wraps `syscall.Lchown` with retry-on-EINTR and path error wrapping.

Important APIs, types, and functions: `Lchown(name string, uid, gid int) error`.

Control flow: calls `syscall.Lchown`; while error is `EINTR`, retries. Non-nil final errors are wrapped in `os.PathError` with operation `lchown`.

State and persistence: mutates symlink/file ownership metadata without following symlinks.

Dependencies and integration points: depends on `os` and `syscall`; used by filesystem metadata application code.

Risks and edge cases: may retry forever if interrupted indefinitely. Permission and platform semantics are passed through as `PathError`.

Test signals: no direct tests in requested files.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/lchown.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/lcow_unix.go -->
# sources/cloud-native/containers-storage/pkg/system/lcow_unix.go

Purpose: reports Linux Containers on Windows unsupported on non-Windows platforms.

Important APIs, types, and functions: `LCOWSupported`.

Control flow: returns false.

State and persistence: no state.

Dependencies and integration points: selected for non-Windows builds. Provides cross-platform API compatibility with Windows implementation.

Risks and edge cases: none beyond always-false behavior.

Test signals: no direct tests in requested files.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/lcow_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/lcow_windows.go -->
# sources/cloud-native/containers-storage/pkg/system/lcow_windows.go

Purpose: reports Windows LCOW support based on initialized package state.

Important APIs, types, and functions: `LCOWSupported`.

Control flow: returns `lcowSupported`, which is initialized from `LCOW_SUPPORTED` in `init_windows.go`.

State and persistence: reads in-memory package-global state; no persistence.

Dependencies and integration points: selected on Windows. Used by callers that conditionally enable Linux-container-on-Windows behavior.

Risks and edge cases: support detection is environment-variable-based and fixed at init time.

Test signals: no direct tests in requested files.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/lcow_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/lstat_unix.go -->
# sources/cloud-native/containers-storage/pkg/system/lstat_unix.go

Purpose: implements Unix `Lstat` returning the package's portable `StatT` abstraction.

Important APIs, types, and functions: `Lstat(path string) (*StatT, error)`.

Control flow: calls `syscall.Lstat` into `syscall.Stat_t`; on error returns an `os.PathError`, otherwise converts with `fromStatT`.

State and persistence: reads filesystem metadata without following symlinks.

Dependencies and integration points: depends on `os` and `syscall`; selected for non-Windows builds. `fromStatT` and `StatT` are defined in other system files.

Risks and edge cases: conversion correctness depends on platform-specific `fromStatT`. Errors are wrapped with operation `"Lstat"`.

Test signals: `lstat_unix_test.go` verifies success for existing files and error/nil stat for missing files.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/lstat_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/lstat_unix_test.go -->
# sources/cloud-native/containers-storage/pkg/system/lstat_unix_test.go

Purpose: tests Unix `Lstat` success and failure behavior.

Important APIs, types, and functions: `TestLstat`.

Control flow: uses `prepareFiles` from other system tests, calls `Lstat` on an existing file and a missing path, and checks non-nil stat on success and nil stat plus error on failure.

State and persistence: creates temporary filesystem entries through shared helpers.

Dependencies and integration points: depends on `testing`; selected on Linux or FreeBSD. It validates `lstat_unix.go` and platform stat conversion.

Risks and edge cases: does not inspect fields of `StatT`; only checks presence/absence.

Test signals: confirms basic error contract for existing versus non-existing paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/lstat_unix_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/lstat_windows.go -->
# sources/cloud-native/containers-storage/pkg/system/lstat_windows.go

Purpose: implements Windows `Lstat` using `os.Lstat` and package stat conversion.

Important APIs, types, and functions: `Lstat(path string) (*StatT, error)`.

Control flow: calls `os.Lstat`; returns error directly on failure; passes the `os.FileInfo` pointer to `fromStatT` on success.

State and persistence: reads filesystem metadata without following symlinks where Windows supports that distinction.

Dependencies and integration points: depends on `os`; selected on Windows. Uses Windows-specific `fromStatT` defined elsewhere.

Risks and edge cases: error wrapping differs from Unix implementation. Conversion takes a pointer to an interface value, matching this package's Windows stat helper expectations.

Test signals: no Windows lstat tests in requested files.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/lstat_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/meminfo.go -->
# sources/cloud-native/containers-storage/pkg/system/meminfo.go

Purpose: defines a portable memory statistics data structure.

Important APIs, types, and functions: `MemInfo` with fields `MemTotal`, `MemFree`, `SwapTotal`, and `SwapFree`.

Control flow: none; data type only.

State and persistence: no state. Instances represent a snapshot of host memory/swap values in bytes.

Dependencies and integration points: platform-specific `ReadMemInfo` implementations populate this type.

Risks and edge cases: field semantics vary by platform source and may not include available/cached memory. Values are int64 bytes.

Test signals: Linux `meminfo_unix_test.go` validates parser population of all four fields.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/meminfo.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/meminfo_freebsd.go -->
# sources/cloud-native/containers-storage/pkg/system/meminfo_freebsd.go

Purpose: implements FreeBSD memory and swap statistics retrieval.

Important APIs, types, and functions: `getMemInfo`, `getSwapInfo`, and `ReadMemInfo`.

Control flow: `getMemInfo` reads `vm.vmtotal`, validates struct size, and combines page size with physical page/free counts. `getSwapInfo` reads swap device count, iterates `vm.swap_info`, validates sizes, and accumulates total and used blocks. `ReadMemInfo` combines memory and swap values and rejects negatives.

State and persistence: reads kernel sysctl state; no mutation.

Dependencies and integration points: depends on cgo FreeBSD headers, `errors`, `fmt`, `unsafe`, and `x/sys/unix`; selected on `freebsd && cgo`.

Risks and edge cases: cgo and exact C struct sizes are required. Swap block/page unit assumptions must match FreeBSD kernel ABI.

Test signals: no FreeBSD meminfo tests in requested files.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/meminfo_freebsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/meminfo_linux.go -->
# sources/cloud-native/containers-storage/pkg/system/meminfo_linux.go

Purpose: implements Linux memory/swap statistics retrieval from `/proc/meminfo`.

Important APIs, types, and functions: `ReadMemInfo` and private `parseMemInfo`.

Control flow: `ReadMemInfo` opens `/proc/meminfo`, defers close, and calls `parseMemInfo`. The parser scans lines, expects at least three fields with `kB`, parses the numeric field, converts KiB to bytes, and records four known keys.

State and persistence: reads procfs snapshot only.

Dependencies and integration points: depends on `bufio`, `io`, `os`, `strconv`, `strings`, and `docker/go-units`. Used by host system reporting and resource calculations.

Risks and edge cases: malformed or unsupported lines are silently skipped. Missing keys leave zero values. Scanner token limits are not customized but proc meminfo lines are small.

Test signals: `meminfo_unix_test.go` verifies correct conversion and skipping malformed lines.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/meminfo_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/meminfo_solaris.go -->
# sources/cloud-native/containers-storage/pkg/system/meminfo_solaris.go

Purpose: implements Solaris memory and swap statistics retrieval through cgo.

Important APIs, types, and functions: C helpers for swap table allocation and kernel page lookup, `getTotalMem`, `getFreeMem`, `ReadMemInfo`, and `getSysSwap`.

Control flow: total/free memory come from `sysconf`. Kernel pages are read through kstat and subtracted from total. Swap stats use `swapctl` to count/list entries, iterate entries, accumulate total/free disk blocks, and free allocated C memory.

State and persistence: reads OS kernel and swap state; no mutation.

Dependencies and integration points: depends on cgo, `fmt`, and `unsafe`; links `kstat`. Selected on `solaris && cgo`.

Risks and edge cases: C helper error paths in `getPpKernel` can leak kstat handles. `getSysSwap` returns block counts scaled by disk blocks per page, which should be reviewed for byte-unit consistency against `MemInfo`.

Test signals: no Solaris tests in requested files.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/meminfo_solaris.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/meminfo_unix_test.go -->
# sources/cloud-native/containers-storage/pkg/system/meminfo_unix_test.go

Purpose: tests Linux `/proc/meminfo` parsing.

Important APIs, types, and functions: `TestMemInfo`.

Control flow: feeds a static multiline meminfo string with four valid kB entries and several malformed entries into `parseMemInfo`, then checks byte conversion using `units.KiB`.

State and persistence: no persistence; parser consumes an in-memory string reader.

Dependencies and integration points: depends on `strings`, `testing`, and `docker/go-units`. It validates the Linux parser without requiring host `/proc`.

Risks and edge cases: does not test scanner errors, missing keys, very large values, or actual `ReadMemInfo` file open.

Test signals: confirms known fields are parsed, units converted to bytes, and malformed lines ignored.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/meminfo_unix_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/meminfo_unsupported.go -->
# sources/cloud-native/containers-storage/pkg/system/meminfo_unsupported.go

Purpose: provides unsupported memory-info implementation for platforms without a concrete reader.

Important APIs, types, and functions: `ReadMemInfo`.

Control flow: returns nil and `ErrNotSupportedPlatform`.

State and persistence: no state and no OS reads.

Dependencies and integration points: selected for platforms other than Linux, Windows, Solaris, and FreeBSD+cgo. Keeps callers compiling while requiring unsupported handling.

Risks and edge cases: comment mentions Linux and Windows even though this build tag also excludes Solaris and FreeBSD+cgo; wording is stale. Callers must handle unsupported errors.

Test signals: no direct tests in requested files.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/meminfo_unsupported.go -->
