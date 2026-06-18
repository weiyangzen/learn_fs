# sources/distributed-fs/ceph-client/tools/testing/ktest/config-bisect.pl

Purpose: Perl helper for bisecting kernel configuration differences between a known-good and known-bad `.config`, producing intermediate configs to test.

Important APIs, types, and functions: command options include `-l` linux tree, `-b` build dir, `-r` reset, and good/bad result labels. Utility functions include `usage()`, `run_command()`, prompt helpers, path expansion, config parsing/saving/comparison helpers, `make_oldconfig()`, `process_new_config()`, `make_half()`, `run_config_bisect()`, and `config_bisect()`.

Control flow: on a new run it copies input good/bad configs to `.tmp` files, optionally prompting before overwrite. On subsequent runs it copies the just-tested build `.config` to either good or bad `.tmp` based on the result label. It normalizes both configs through `make olddefconfig` with fallbacks to `oldnoconfig` or `yes '' | make oldconfig`, reads them into hashes, computes differences, attempts top or bottom halves of bad values into good config or good values into bad config, regenerates `.config`, and stops when it has a non-identical intermediate ready to test. If no further split is possible, it prints remaining differences and exits with failure.

State and persistence: persists bisection state in `<good>.tmp`, `<bad>.tmp`, and the build directory `.config`. It rewrites the temporary config files each run.

Dependencies and integration points: depends on Perl, kernel `make` config targets, a kernel tree/build dir, and user test feedback between runs. It is an adjunct to ktest/manual build bisection.

Risks: hash key order is unordered, so split halves may not be deterministic across Perl versions/settings. It may not isolate dependency-only differences well despite tracking configs that appear only in one file. It rewrites `.config` and temp files, so paths must not be the original only copies. Some variables (`config_ignore`, dependency helpers) are present but not fully used in the viewed control path.

Test signals: after initial invocation, the build `.config` should be ready to test and temp good/bad files should exist. Re-running with `good` or `bad` should narrow differences until a single or unsplittable set remains.
