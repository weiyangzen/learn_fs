# sources/cloud-native/composefs-rs/crates/composefs/src/util.rs

Purpose: central utility module for digest I/O adaptation, file-descriptor helpers, exact-ish reads, SHA-256 parsing, errno filtering, temporary-name generation, and atomic symlink replacement.

Important APIs/types/functions: `DigestWrite<D>`, `DigestWrite::finalize`, `proc_self_fd`, `reopen_tmpfile_ro`, `create_tmpfile_in`, `read_exactish`, `read_exactish_async`, `Sha256Digest`, `parse_sha256`, `ErrnoFilter`, `generate_tmpname`, and `replace_symlinkat`.

Control flow: `read_exactish` loops until a buffer is full, distinguishes clean EOF from partial EOF, and retries `Interrupted`; the async form mirrors this with Tokio. `replace_symlinkat` first tries direct creation, then no-ops if an existing symlink already points to the target, otherwise creates a randomized temporary symlink and atomically renames it into place.

State/persistence: `create_tmpfile_in` creates anonymous `O_TMPFILE` state and `reopen_tmpfile_ro` transitions it for fs-verity. `replace_symlinkat` persists symlink targets atomically in a directory fd. Random temporary names are process-local and not persisted except during replacement.

Dependencies/integration: uses `rustix` for fd-relative filesystem operations, `sha2` for digest types, `tokio` for async reads, `rand` for temp names, and Unix path byte access. It supports repository object writes, splitstream parsing, fs-verity enablement, and link replacement.

Risks/test signals: tests cover clean EOF, partial EOF, broken readers, async behavior, and SHA-256 parsing including case and length errors. Remaining risks include 16-attempt temporary-name collision exhaustion, fd/path assumptions through `/proc/self/fd`, and callers misusing `parse_sha256` for non-SHA256 algorithms.
