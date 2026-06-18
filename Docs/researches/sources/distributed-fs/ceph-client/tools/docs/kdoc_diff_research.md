<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/docs/kdoc_diff -->
# sources/distributed-fs/ceph-client/tools/docs/kdoc_diff

Purpose: Compares `kernel-doc` output between two Git commits, with optional full-tree scanning, explicit file selection, cache cleanup, and YAML regression checking.

Important APIs/types/functions: `GitHelper` validates repository state and checks out commits. `CacheManager` creates `.doc_diff_cache` subdirectories and maps refs to short-hash cache paths. `KernelDocRunner` finds `.. kernel-doc::` references, generates man/RST logs, emits YAML, and runs `tools/unittests/test_kdoc_parser.py`. `DiffManager` compares cached output directories. `SignalHandler` restores the original branch on normal exit or signals. `parse_commit_range()` accepts `old..new` or `old`.

Control flow: `main()` parses commits and file options, refuses `--full` with explicit file lists, initializes cache, validates clean Git state, picks scan mode (`full`, `partial`, or `no-cache`), then within `SignalHandler` checks out old and new commits to generate or reuse outputs. Non-regression mode diffs cached directories; regression mode generates YAML from the old commit and runs unit tests against the new commit.

State and persistence: Persistent state lives in `.doc_diff_cache/full`, `.doc_diff_cache/partial`, and `.doc_diff_cache/no_cache`, plus temporary `__tmp__`. The script temporarily mutates the working tree by forced Git checkout, but refuses to run with uncommitted changes and restores the original branch.

Dependencies/integration: Depends on Git, `tools/docs/kernel-doc`, kernel `Documentation/**/*.rst`, `diff`, and the kernel-doc parser unit test. It is a developer validation tool rather than a build step.

Risks/tests: The highest risk is destructive checkout behavior if repository cleanliness detection misses ignored or external state. Other risks include stale caches hiding changes, unhandled detached-HEAD restoration, and `run_unittest()` returning success even when the subprocess returns nonzero. Test signals are clean-repo dry runs over a small file set, `--clean`, `--full`, `--regression`, signal interruption, and cache reuse.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/docs/kdoc_diff -->
