# sources/compression/xz/src/scripts/xzmore.in

## Purpose
Template for `xzmore`, viewing decompressed files through `more` or `$PAGER` with interactive prompts between files.

## Important APIs, Types, And Functions
Variables:
- `xz='@xz@ --format=auto'`.
- `oldtty`, `cb`, and `ncb` manage terminal mode.
- `FIRST`, `FILE`, and `ANS` implement multi-file prompting.

## Control Flow
The script handles `--help` and `--version`, saves terminal settings, sets traps to restore terminal mode, and either reads stdin or iterates files. With no args and tty stdin it prints usage and exits 1; otherwise it pipes decompressed stdin to `${PAGER:-more}`. For multiple files it prompts before subsequent files, lets `e`/`q` exit and `s` skip, prints a file banner, and pipes `xz -cdfqQ -- "$FILE"` to the pager.

## State And Persistence
Temporarily changes terminal mode and restores it via traps. No persistent filesystem state.

## Dependencies And Integration Points
Configured shell/xz/package placeholders. Depends on `stty`, `dd`, `more`/`PAGER`, and xz. Installed via scripts Automake rules.

## Risks
Uses `eval "${PAGER:-more}"`, so pager environment content is executed as shell code by design. Terminal restoration must work across signals. File readability check uses `true < "$FILE"`. `XZ_OPT` is preserved.

## Test Signals
No-arg tty and pipe modes, single and multiple files, prompt responses `q/e/s/other`, terminal restore on signals, custom `PAGER`, unreadable file, and `--help`/`--version`.
