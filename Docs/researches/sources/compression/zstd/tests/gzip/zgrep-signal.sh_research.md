<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/gzip/zgrep-signal.sh -->
## sources/compression/zstd/tests/gzip/zgrep-signal.sh

Purpose: Verifies `zgrep` terminates gracefully when its output pipeline gets a signal such as SIGPIPE.

Important APIs and functions: Sources `init.sh`; uses Perl with POSIX `dup2` to implement `write_to_dangling_pipe`; invokes `cat` and `zgrep`; uses `skip_`, `framework_failure_`, and `Exit`.

Control flow: It creates `f.gz`, verifies Perl can manipulate file descriptors, then runs `cat f.gz f.gz` with stdout connected to a pipe with the read end closed to learn the host's signal exit status. It then runs `zgrep a f.gz f.gz` in the same dangling-pipe setup and requires the same signal-derived status.

State and persistence: Creates `f.gz` in the temporary test directory.

Dependencies and integration points: Depends on a suitable Perl and POSIX signal semantics. Exercises `zgrep`'s pipeline signal propagation rather than content correctness.

Risks: Signal status conventions vary; the script calibrates with `cat`, but shells or Perl implementations that ignore SIGPIPE can cause skip or framework failure. This is intentionally Unix-specific.

Test signals: `zgrep` must exit with the calibrated signal status greater than `128`.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/gzip/zgrep-signal.sh -->
