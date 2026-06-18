# sources/distributed-fs/openafs/src/tests/write-ro-file.c

Purpose: verifies that a basic create/write/close/unlink sequence can complete in the current directory. Despite the name, it is a writable-file smoke test likely paired with read-only volume checks elsewhere.

Important APIs and functions: `main` opens `foo` with `O_RDWR | O_CREAT` and mode `0`, writes three bytes `"foo"`, closes the descriptor, then unlinks the file. On write or close failure it attempts to unlink before reporting via `err`.

Control flow/state: the only persistent artifact is `foo`, removed on normal and most error paths. Dependencies are POSIX `open`, `write`, `close`, `unlink`, and `err`.

Risks: using create mode `0` means permissions are no-access after creation, though the already-open descriptor remains writable. The code treats short positive writes as success because it only checks `< 0`, so a partial write would pass. Test signal is exit code and absence of syscall errors, not content verification.
