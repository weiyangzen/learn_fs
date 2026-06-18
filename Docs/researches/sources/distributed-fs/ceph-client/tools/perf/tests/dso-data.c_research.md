# sources/distributed-fs/ceph-client/tools/perf/tests/dso-data.c

Purpose: `dso-data.c` tests DSO file data reads, cache behavior, descriptor limit handling, and reopen behavior.

Important APIs and state: `test_file` creates patterned temporary files. `dso__data_fd`, `dso__data_read_offset`, `dso__data_close`, `reset_fd_limit`, `dsos__add`, and `dsos__exit` are exercised. Three test cases are registered under `"DSO data tests"`: read, cache, and reopen.

Control flow: the read test creates a large file, wraps it in a DSO, reads offsets across cache pages and file end, and verifies bytes. The cache test lowers `RLIMIT_NOFILE`, creates many DSOs, opens enough data fds to force LRU closing, reads some DSOs, and checks no fd leaks. The reopen test sets a tight fd limit, opens DSOs plus an extra fd, and verifies older DSO fds are closed and later reopened as needed.

State and persistence: temporary files are created and unlinked; process fd limits are modified during tests. DSO containers and references are released.

Dependencies, integration, risks, and tests: it depends on `/tmp`, `/proc/self/fd`, procfs mount discovery, and ability to adjust rlimits. Risks include fd-limit side effects, early-return cleanup gaps, and environment-specific open-fd baselines. Test signals are exact byte reads, expected DSO fd eviction, and equal open-fd counts before/after.
