<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine-tests/src/cli_tools.rs -->
# sources/control-plane/mayastor/io-engine-tests/src/cli_tools.rs

Purpose: Shared subprocess execution utility for test helpers that need external host commands.

Important APIs: `run_command_args(path, args, short_desc)` builds a `Command` then delegates to `run_command`; `run_command(cmd, desc, short_desc)` spawns, waits, joins an output reader thread, and returns exit status plus output lines as `OsString`; `spawn_child()` configures stdout/stderr piping and creates the child plus reader thread.

Control flow: stdout and stderr are merged by setting stderr to stdout. The reader consumes lines using `BufReader::read_until(b'\n')`, optionally echoes them prefixed by `short_desc`, and preserves raw bytes through `OsStringExt`.

State and dependencies: no persistent state; depends on host process spawning, pipes, and Unix `OsString` byte conversion.

Risks and test signals: commands can deadlock only if output reading stops, but the dedicated thread mitigates this. It does not treat nonzero exit as an error; callers must inspect `ExitStatus`. The raw-byte line handling is robust for non-UTF8 command output.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine-tests/src/cli_tools.rs -->
