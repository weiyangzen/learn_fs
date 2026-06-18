# File Research: sources/block-storage/util-linux/sys-utils/dmesg.c

## Scope

Implements `dmesg`, a full-featured kernel ring-buffer display and control utility. It can read `/dev/kmsg`, syslog/klogctl buffers, or files; parse kernel records; filter by facility/level/time; format timestamps; output raw/text/JSON; colorize; page output; follow new records; clear the buffer; and set console logging controls.

## Public And Internal APIs Covered

- Main command-line entry point.
- Buffer backends: `init_kmsg()`, `read_kmsg_one()`, `read_syslog_buffer()`, `mmap_file_buffer()`, `prepare_buffer()`, `release_buffer()`.
- Parsers: `parse_level()`, `parse_facility()`, `parse_faclev()`, `parse_syslog_timestamp()`, `parse_kmsg_timestamp()`, `parse_callerid()`, `get_next_syslog_record()`, `parse_kmsg_record()`.
- Filtering/time: `record_time()`, `accept_record()`, `record_localtime()`, `record_ctime()`, `iso_8601_time()`, `record_count_delta()`.
- Formatting/output: `print_record()`, `print_buffer()`, `print_kmsg()`, `print_kmsg_file()`, `raw_print()`, `safe_fwrite()`.
- Time format management: `reset_time_fmts()`, `include_time_fmt()`, `exclude_time_fmt()`, `replace_time_fmt()`, `replace_delta_fmt()`, `which_time_format()`.

## Control Flow And Behavior

- Default read method is `/dev/kmsg`; if unavailable, it falls back to syslog/klogctl.
- `--file` reads syslog-style buffers via mmap; `--kmsg-file` reads `/dev/kmsg` record format from a file.
- `/dev/kmsg` records are parsed as `faclev,seq,timestamp[,optional...];message`, including optional `caller=` metadata when present.
- Syslog-style records parse `<facility.priority>` and `[seconds.useconds]` prefixes when needed for filters/decode/color/JSON/time.
- Filtering supports:
  - levels/priorities by number or name,
  - facilities by number or name,
  - kernel-only/userspace-only facility masks,
  - `--since` / `--until` wall-clock timestamps.
- Timestamp formats include raw monotonic time, ctime, ctime+delta, delta-only, relative time, ISO-8601, and no timestamp. Combination rules merge delta with ctime/raw formats and resolve `--notime` conflicts.
- Human mode enables relative time, color auto mode, and pager by default.
- JSON mode disables raw/pager/escaping behavior, resets time formatting, and emits a `dmesg` array of objects.
- Color output highlights timestamps, subsystem prefixes, warning/error levels, and messages containing `segfault at`.
- `--force-prefix` repeats prefixes on each line of multi-line kmsg messages and is only allowed for kmsg.
- Control actions use klogctl for clear, read-clear, console on/off, and console level.

## State And Data Structures

- `struct dmesg_control` stores filter bitsets, last timestamp, boot/suspended time, selected action/method, buffer state, kmsg fd and first read, time format list, JSON writer, output mode flags, and caller-id width.
- `struct dmesg_record` stores message pointer/size, level/facility, timestamp, caller id, and parser cursor state.
- Static level and facility tables mirror syslog priority/facility names.
- Static color table maps semantic dmesg color roles to terminal color schemes.

## Dependencies

- Linux syslog/klogctl API and `/dev/kmsg`.
- util-linux helpers for colors, pager, JSON writing, timestamp parsing, monotonic/boot time, mangle decoding, safe I/O, bit arrays, option exclusion, and wide-character handling.
- `/proc/sys/kernel/pid_max` for caller-id field width estimation.

## Risks And Invariants

- `/dev/kmsg` read uses `PRINTK_MESSAGE_MAX + 1` so the kernel does not reject records as too small.
- `read_kmsg_one()` retries on `EPIPE` because records can change while reading.
- Raw syslog filtering is only allowed with `/dev/kmsg`; other raw buffers cannot be reliably filtered.
- mmap file handling progressively unmaps already printed pages to reduce memory use.
- Wall-clock timestamps depend on boot time and suspended-time estimation and can be inaccurate around suspend/resume.
- JSON mode intentionally changes several formatting flags to produce valid machine-readable output.
