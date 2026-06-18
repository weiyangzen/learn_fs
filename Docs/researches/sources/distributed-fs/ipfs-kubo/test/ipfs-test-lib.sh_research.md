## sources/distributed-fs/ipfs-kubo/test/ipfs-test-lib.sh

Purpose: generic shell helper library shared by sharness tests, with comparison utilities, Docker wrappers, portable sequence/base64 helpers, and safer command quoting.

Important functions and control flow: `ansi_strip`, `shellquote`, `test_fsh`, `test_cmp`, `test_sort_cmp`, and `test_path_cmp` normalize diagnostics and comparisons. Docker helpers wrap build/run/exec/stop/rm/rmi. `test_includes_lines` validates expected-line subsets; `test_seq` avoids depending on GNU seq; `b64decode` chooses platform-specific base64 flags.

State and dependencies: writes temporary sorted/standardized comparison files next to inputs and operates on Docker state when used. It depends on sed, diff, sort, comm, docker, expr, uname, and base64.

Risks: helper behavior is global to many shell tests, so changes can alter diagnostics or comparison semantics broadly. `shellquote` and `eval` in `test_fsh` must stay correct for arguments with quotes. Test signals come from `t0015-basic-sh-functions.sh` and broad use across the sharness suite.
