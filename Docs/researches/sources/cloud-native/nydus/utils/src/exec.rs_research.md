# sources/cloud-native/nydus/utils/src/exec.rs

Purpose: small shell-command execution helper with optional stdin and captured output.

Important APIs/types/functions: `exec(cmd: &str, output: bool, input: &[u8]) -> Result<String>` runs `sh -c cmd` with `RUST_BACKTRACE=1`, optional piped stdin, and either captured or inherited stdout/stderr.

Control flow: the function configures a child process, writes input if provided, waits for completion, returns captured stdout when `output` is true, and maps non-zero exits to `eother!("exit with non-zero status")`. Captured stdout must be valid UTF-8.

State and persistence: no internal state. External commands can modify arbitrary system state depending on `cmd`.

Dependencies and integration points: used by utility callers needing shell integration. Depends on std process APIs and project logging/error macros.

Risks: command string is executed through the shell, so callers must avoid passing unsanitized user input. Non-zero stderr is discarded from error messages when captured. Captured stdout requiring UTF-8 limits binary commands. `output=false` inherits process output, which can noisy-log tests or daemons.

Test signals: tests cover captured echo, inherited echo, stdin piping through `cat`, and non-zero exit errors for both output modes.
