# File Research: sources/block-storage/lvm2/tools/lvmcmdlib.c

## Purpose
Implements the public `liblvm2cmd` API declared in `lvm2cmd.h`.

## Main Functions
- `cmdlib_lvm2_init(static_compile, threaded)`:
  - Sets static-build state.
  - Calls `init_lvm(1, 1, threaded)`.
  - Registers commands.
  - Returns a `struct cmd_context *` as an opaque handle.
- `lvm2_run(handle, cmdline)`:
  - Creates a one-off handle with `lvm2_init()` if `handle` is `NULL`.
  - Duplicates and splits the command line with `lvm_split()`.
  - Rejects empty commands and too many arguments.
  - Handles temporary internal command strings:
    - `_memlock_inc`
    - `_memlock_dec`
    - `_dmeventd_thin_command`
    - `_dmeventd_vdo_command`
  - Otherwise delegates to `lvm_run_command()`.
- `lvm2_disable_dmeventd_monitoring()` marks the context as dmeventd-run.
- `lvm2_log_level()` adjusts default verbosity.
- `lvm2_log_fn()` installs the logging callback.
- `lvm2_exit()` finalizes the command context.

## Important Details
- One-off execution cleans up with `lvm2_exit()` before returning.
- The API passes internal `ECMD_*`-style return codes, matching constants in the public header.
- Command splitting is shell-like but simple, inherited from `lvmcmdline.c`.

## Dependencies
- Tool context setup and teardown.
- Label and memlock subsystems.
- Public `tools/lvm2cmd.h`.
