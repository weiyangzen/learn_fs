# sources/compression/zstd/tests/automated_benchmarking.py

## Purpose

This Python script benchmarks zstd builds for open pull requests or local/current builds and reports compression/decompression speed regressions.

## Important APIs, Types, and Functions

It fetches PR metadata from GitHub with `get_new_open_pr_builds`, identifies latest merge hashes, clones/builds repos with `clone_and_build`, parses benchmark output, benchmarks individual files or dictionary directories, computes regressions, and drives modes through `main`. CLI options include directory, levels, iterations, emails, frequency, mode, and dictionary file.

## Control Flow, State, and Persistence

In current mode it builds the parent repo; in fast/onetime/continuous modes it chooses release or open PR builds. It runs `zstd -qb<level>` repeatedly and keeps the maximum speed across iterations. Continuous mode sleeps between checks. It persists previous PR state in `prev_prs.pk` and creates clone directories named for user/hash.

## Dependencies and Integration Points

It depends on GitHub API access, git, make, Python stdlib modules, zstd benchmark output format, and optionally `mutt` for email alerts. It is wired into `tests/Makefile` target `automated_benchmarking`.

## Risks and Test Signals

Risks include unauthenticated GitHub API rate limits, `os.system` command interpolation, broad `rm -rf zstd-{user}-{sha}`, fragile parsing by splitting on spaces and locating `MB/s`, and an apparent early `return regressions` indentation inside the dictionary loop. Tests should cover output parsing fixtures, clone path construction, no-file handling, current/onetime modes, dictionary regressions, and failure behavior when API/build commands fail.
