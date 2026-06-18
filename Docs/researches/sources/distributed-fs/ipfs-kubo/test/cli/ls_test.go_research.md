# sources/distributed-fs/ipfs-kubo/test/cli/ls_test.go

Purpose: validates `ipfs ls --long` formatting for mode, mtime, size, headers, directories, and stable output.

Important APIs/functions: `TestLsLongFormat` creates filesystem fixtures, uses `ipfs add` with `--preserve-mode` and/or `--preserve-mtime`, copies files into MFS where needed, and inspects `ipfs ls` output.

Control flow: parallel subtests create known files/directories with explicit modes and timestamps, add them recursively or as single files, obtain directory CIDs, run `ls --long` with combinations of `--headers` and `--size=false`, then assert columns and substrings/regexes.

State and persistence: temp files are written in node repos; blockstore and MFS state are mutated by add/cp/stat commands. Timestamps are fixed in the past to avoid current-year formatting variance.

Dependencies/integration: depends on OS file modes/mtime, Kubo UnixFS import metadata preservation, and CLI output formatting.

Risks: Unix permission rendering may differ on non-Unix systems; output parsing with whitespace fields can be sensitive to date format spacing. Test signals are mode strings, header order, CID prefixes, numeric size fields, date tokens, trailing slash for directories, and filename presence.
