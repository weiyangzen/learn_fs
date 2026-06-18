# File Research: sources/cow-pools/nilfs-utils/sbin/nilfs-clean.c

## Purpose
`nilfs-clean.c` implements the `nilfs-clean` command, a CLI controller for NILFS2 garbage collection/cleaner service behavior. It can run cleaner work, query status, suspend/resume, reload configuration, stop, or shut down the cleaner.

## Main Interfaces
- Includes NILFS userland APIs from `nilfs.h`, `nilfs_cleaner.h`, `parser.h`, and `util.h`.
- Uses `nilfs_cleaner_open`, `nilfs_cleaner_run`, `nilfs_cleaner_get_status`, `nilfs_cleaner_suspend`, `nilfs_cleaner_resume`, `nilfs_cleaner_reload`, `nilfs_cleaner_stop`, and `nilfs_cleaner_shutdown`.
- Opens the raw filesystem through `nilfs_open` only for speed auto-adjustment.

## Command Model
Supported commands are encoded in `clean_cmd`:
- `NILFS_CLEAN_CMD_RUN`: default cleaner run request.
- `NILFS_CLEAN_CMD_INFO`: print `idle`, `running`, `suspended`, or unknown status.
- `NILFS_CLEAN_CMD_SUSPEND`
- `NILFS_CLEAN_CMD_RESUME`
- `NILFS_CLEAN_CMD_RELOAD`
- `NILFS_CLEAN_CMD_STOP`
- `NILFS_CLEAN_CMD_SHUTDOWN`

Options include:
- `-b` / `--break` / `--stop`: stop running cleaner.
- `-c [conffile]` / `--reload[=CONFFILE]`: reload cleaner config.
- `-l` / `--status`: status query.
- `-p SECONDS`: protection period via `nilfs_parse_protection_period`.
- `-m COUNT[%]`: minimum reclaimable blocks, absolute or percent.
- `-S COUNT[/SECONDS]`: cleaner speed, as segments per interval.
- `-q`, `-r`, `-s`, `-v`, `-V`, `-h`.

## Core Behavior
- `main` installs `nilfs_clean_logger` into `nilfs_cleaner_logger`, parses options, handles version output, validates an optional device/node argument with `stat`, and calls `nilfs_do_clean`.
- `nilfs_do_clean` opens a cleaner queue, temporarily installs signal handlers for `SIGINT`, `SIGTERM`, and `SIGHUP`, dispatches the selected request, then closes the cleaner handle.
- Signal interruption uses `sigsetjmp`/`siglongjmp` through `nilfs_clean_escape`.
- `nilfs_clean_do_run` builds `struct nilfs_cleaner_args` with one pass, interval, segments per clean, optional protection period, and optional minimum reclaimable threshold.

## GC Speed Handling
- Default target GC throughput is `1.28 GiB/s`.
- If `-S` did not set `nsegments_per_clean`, `nilfs_clean_adjust_speed` opens the device read-only/raw, reads block size and blocks per segment, derives bytes per segment, and converts the default throughput into segments per cleaner call.
- Result is clamped to `[1, 32]` segments per call.
- If layout data cannot be read or arithmetic would overflow, fallback is `16` segments per call.

## Parsing Details
- `nilfs_clean_parse_gcspeed` accepts `COUNT`, `COUNT/SECONDS`, and fractional interval syntax such as `COUNT/0.5`.
- `nilfs_clean_parse_min_reclaimable` accepts `COUNT` or `COUNT%`, rejects percentages above 100, and stores the unit separately.
- Invalid or overflowing values terminate with diagnostics.

## Notable Risks and Edge Cases
- The logger filter suppresses messages with priority `>= LOG_INFO`; the `verbose` branch also suppresses priorities greater than `LOG_INFO`, so verbose mode does not obviously enable informational logging from this wrapper.
- `strtod` fractional interval conversion stores nanoseconds through floating-point arithmetic; small precision effects are possible but low impact.
- `nsegments_per_clean` from `-S` is not clamped to the same min/max range as auto-adjusted values.
- The command allows no device argument, leaving device discovery to `nilfs_cleaner_open`.
