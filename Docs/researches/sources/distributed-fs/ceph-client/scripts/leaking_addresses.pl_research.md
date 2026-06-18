# sources/distributed-fs/ceph-client/scripts/leaking_addresses.pl

## Purpose
`leaking_addresses.pl` scans a running system's `/proc`, `/sys`, and `dmesg` output for strings that look like leaked kernel addresses, with optional raw-output capture and summary reporting.

## Important APIs, Types, and Functions
Options include `--output-raw`, `--input-raw`, `--raw`, `--suppress-dmesg`, `--squash-by-path`, `--squash-by-filename`, `--kernel-config-file`, `--kallsyms`, `--32-bit`, `--page-offset-32-bit`, `--debug`, and `--help`.

Important functions are `help()`, `dprint()`, architecture helpers, `get_kernel_config_option()`, `option_from_file()`, `is_false_positive()`, `is_false_positive_32bit()`, `get_page_offset()`, `is_in_vsyscall_memory_region()`, `may_leak_address()`, `get_address_re()`, `get_x86_64_re()`, `parse_dmesg()`, `skip()`, `timed_parse_file()`, `parse_binary()`, `parse_file()`, `check_path_for_leaks()`, `walk()`, `format_output()`, `dump_raw_output()`, `parse_raw_file()`, `print_dmesg()`, `squash_by()`, and cache helpers.

## Control Flow
The script parses options, handles raw-input formatting mode, validates architecture support, optionally redirects stdout to a raw output file, optionally loads nonzero kallsyms addresses for binary scanning, scans `dmesg`, then recursively walks `/proc` and `/sys`. Each readable text file is scanned line by line; selected binary paths are ignored or scanned for packed kallsyms addresses. Formatting mode reads a prior raw file and either dumps raw output or prints summaries.

## State and Persistence
Runtime state includes skip lists, loaded kallsyms, architecture/config-derived regex decisions, and summary caches. Persistent outputs are optional raw result files. It reads live system state and kernel config sources such as `/proc/config.gz` or `/boot/config-*`.

## Dependencies and Integration Points
Depends on Perl modules `POSIX`, `File::Basename`, `File::Spec`, `File::Temp`, `Cwd`, `Term::ANSIColor`, `Getopt::Long`, `Config`, `bigint`, and `feature state`; external commands include `uname`, `dmesg`, and `gunzip`. It is a kernel hardening/debugging utility rather than a build dependency.

## Risks and Edge Cases
Scanning `/proc` and `/sys` can block or be expensive, so per-file alarm timeout is used. PID directories except `/proc/1` are skipped by design. Address regexes are architecture-specific and can generate false positives/negatives. The source contains a duplicated `push @dirs, $path;`, causing directories to be queued twice and potentially increasing scan cost. Binary scanning with large files and many kallsyms can be slow.

## Test Signals
Use raw input fixtures for summary modes, synthetic text containing known false positives and true positives, mocked config files for 32-bit/5-level paging, and limited directory trees for walk/skip behavior.
