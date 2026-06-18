# File Research: sources/block-storage/lvm2/tools/lvm.c

## Purpose
`lvm.c` is the main executable entry point for the `lvm` CLI and, when readline/editline support is enabled, implements the interactive `lvm>` shell.

## Main Behavior
- `main()` delegates directly to `lvm2_main(argc, argv)` from the command-line subsystem.
- Interactive shell support is compiled only under `READLINE_SUPPORT` or `EDITLINE_SUPPORT`.
- Shell completion uses `_cmdline` metadata:
  - `_list_cmds()` completes command names.
  - `_list_args()` completes short and long options valid for the detected first command word.
  - `_completion()` dispatches between command completion and option completion.
- History is stored at `$HOME/.lvm_history`, read on shell startup, stifled to `shell_history_size`, and written after command execution.

## Shell Execution Flow
`lvm_shell()`:
- Initializes report formatting and command-log report state.
- Reads lines with `readline("lvm> ")`.
- Handles EOF, empty lines, optional leading `lvm`, and `quit`/`exit`.
- Splits command text with `lvm_split()`.
- Runs `lvm_run_command()`.
- Converts `ENO_SUCH_CMD` into user-facing shell errors.
- Records command success/failure into the command log report.
- Flushes grouped reports with `dm_report_group_output_and_pop_all()`.
- Cleans report handles and restores previous log report state on exit.

## Important Details
- The shell avoids retaining log rows across normal commands by calling `_discard_log_report_content()`.
- `lastlog` is special: it keeps command log content and temporarily changes report selection.
- `cmd->is_interactive` gates command-line options marked noninteractive.
- Shell memory cleanup is explicit: `free(input)`, `dm_report_group_destroy()`, and `dm_report_free()`.

## Dependencies
- `lvm2cmdline.h` for `lvm2_main`, `lvm_run_command`, `lvm_split`, and command metadata.
- Readline/editline APIs for history and completion.
- LVM report/log APIs for shell command logging.
