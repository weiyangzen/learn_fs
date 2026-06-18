# sources/distributed-fs/ceph-client/tools/memory-model/scripts/parseargs.sh

Purpose: Provides common argument parsing and default `LKMM_*` environment setup for Linux Kernel Memory Model scripts.

Important APIs and functions: Intended to be sourced. `initparam name default` sets and exports defaults while preserving caller-provided values and recording `<name>_DEF`. `usagehelp`, `usage`, and `checkarg` implement shared diagnostics. Supported options include `--destdir`, `--herdopts`, `--hw`, `--jobs`/`-j`, `--procs`, and `--timeout`.

Control flow: The script initializes defaults, loops through argv, validates option arguments with regex allow/deny patterns, creates and permission-checks `LKMM_DESTDIR`, exports parsed variables, derives `LKMM_TIMEOUT_CMD`, and removes its temporary directory.

State and persistence behavior: It mutates the caller shell environment and can create the destination directory. Temporary shell snippets under `/tmp/parseargs.sh.$$` are removed at completion.

Dependencies and integration points: Sourced by init/new/run scripts; downstream scripts rely on exported `LKMM_DESTDIR`, `LKMM_HERD_OPTIONS`, `LKMM_HW_MAP_FILE`, `LKMM_JOBS`, `LKMM_PROCS`, `LKMM_TIMEOUT`, and `LKMM_TIMEOUT_CMD`.

Risks: It uses generated shell code in `initparam`. Some paths and options are only regex-validated, not shell-escaped. `mkdir $LKMM_DESTDIR` is unquoted in one spot, making whitespace paths risky.

Test signals: Source it with defaults and each option, including invalid numbers/timeouts and existing or new destination directories; assert exported variables and usage failures.
