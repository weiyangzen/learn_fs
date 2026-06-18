# sources/distributed-fs/openafs/src/tests/write-ucc.c

Purpose: stresses updates to file contents plus metadata changes before close. The name suggests write/update/chmod/chown or cache consistency coverage.

Important APIs and functions: `doit` opens a target file for write/create/truncate, writes `"hej\n"`, sets access and modification times with `utimes`, changes mode to `0644`, attempts `chown(filename, 0, 0)` without enforcing success, checks size with `fstat` while the fd is open, closes, then checks size again with `stat`. `main` accepts an optional filename defaulting to `blaha`.

State and integration: the file remains after the test with size four and mode `0644` if `chmod` succeeds. It depends on POSIX metadata syscalls and is relevant to AFS client store-status/writeback sequencing.

Risks/test signals: ignoring `chown` errors is intentional for non-root test runs but means ownership semantics are not verified. It catches short writes and size mismatches before and after close, which are good signals for delayed AFS writeback/cache consistency issues.
