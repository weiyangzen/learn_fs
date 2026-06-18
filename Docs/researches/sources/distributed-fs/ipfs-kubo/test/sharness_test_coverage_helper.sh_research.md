## sources/distributed-fs/ipfs-kubo/test/sharness_test_coverage_helper.sh

Purpose: shell utility that estimates sharness command coverage by matching `ipfs commands --flags` output against `ipfs` invocations in sharness test files.

Important functions and control flow: parses `-h/--help` and `-v/--verbose`, creates a timestamped temp directory, uses `git grep` to collect sharness lines containing `ipfs`, filters out test descriptions, comments, variable definitions, grep/cat/rmdir/echo false positives, and `/ipfs` or `.ipfs` path references, then calls `ipfs commands --flags`. `reverse` abstracts `tac` versus `tail -r`. `process_command` builds regexes for command/subcommand paths, counts matching test files by sharness prefix, and appends coverage summaries. It also produces a file of matched command lines for diffing.

State and persistence: writes all intermediate files under `/tmp/coverage_helper.<timestamp>.*`; it does not clean the temp directory despite the trailing comment. It requires running from the test tree layout where `sharness/t*-*.sh` exists.

Dependencies and integration points: depends on POSIX shell plus `git`, `egrep`, `sed`, `cut`, `sort`, `uniq`, `expr`, and a built `ipfs` binary in PATH. It integrates with CLI command discovery rather than static command registries.

Risks and test signals: regex filtering can undercount/overcount commands, especially multiline shell, helper aliases, variable-expanded subcommands, or changed sharness paths. Useful as a heuristic coverage report, not a precise test oracle.
