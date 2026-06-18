## sources/distributed-fs/tahoe-lafs/benchmarks/test_cli.py

Purpose: measures basic Tahoe CLI put/get latency against the benchmark grid.

Important tests/fixtures: autouse `cli_alias` creates alias `cli`; `test_get_put_files_sequentially` is parametrized over file sizes from 1 KB to 10 MB.

Control flow: for each size, it builds deterministic bytes, records a benchmark block for five sequential `tahoe put - cli:<name>` subprocesses with stdin data, then records five sequential `tahoe get cli:<name> -` subprocesses and verifies stdout matches.

State and dependencies: writes files into the Tahoe grid through the client node alias. Depends on the `tahoe` CLI in PATH, benchmark fixtures, subprocess pipes, and integration util `cli`.

Risks: subprocess I/O errors can deadlock if commands misbehave, though data sizes are modest. File names include loop indexes but not file size, so repeated parameter cases share prefixes and rely on overwrite or independent caps semantics.
