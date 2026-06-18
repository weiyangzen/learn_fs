# sources/compression/zstd/tests/test_process_substitution.bash

Purpose: This Bash test verifies zstd's `--filelist` support when the file list path is supplied through Bash process substitution.

Important APIs and commands: It accepts an optional first argument selecting the zstd executable, defaulting to `zstd`. It uses `rm`, `mkdir`, `echo`, `find`, `sort`, process substitution `<(...)`, output redirection, `grep`, and zstd compression/decompression flags `--filelist`, `-c`, `-d`, and `-o`.

Control flow: The script enables `set -e`, creates `tmp_process_substit` with three text files, removes prior artifacts, and runs five tests. Test 1 passes a sorted `find` output as a process-substitution file list. Test 2 passes an `echo -e` list. Test 3 writes a filelist then passes `cat` through process substitution. Test 4 decompresses the combined output and greps for all three expected file contents. Test 5 passes an empty list and accepts either graceful output creation or proper rejection. It then removes the temporary directory.

State and persistence: Temporary state is confined to `tmp_process_substit` and removed at the end on success. If a command fails before cleanup, the temp directory can remain for diagnosis.

Dependencies and integration points: Requires Bash specifically because POSIX `sh` does not support process substitution. It depends on zstd archive behavior for multiple files listed through `--filelist` and on decompression producing a combined output file.

Risks and test signals: The script uses Unicode check/cross symbols in output, unlike most source files. `echo -e` behavior is shell-dependent but Bash is explicit. `set -e` plus `|| true` intentionally tolerates the empty-list case. Success prints each pass message and "All tests completed successfully!".
