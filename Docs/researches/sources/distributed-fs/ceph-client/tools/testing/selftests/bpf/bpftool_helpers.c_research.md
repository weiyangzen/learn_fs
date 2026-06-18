# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/bpftool_helpers.c

Purpose: helper for running bpftool commands from selftests with automatic bpftool path discovery.

Important APIs and functions: `detect_bpftool_path()` checks `$BPFTOOL`, `./tools/sbin/bpftool`, and `../tools/sbin/bpftool`; `run_command()` caches the detected path, builds a command string, runs it with `popen`, optionally captures output, and closes it. Public wrappers are `run_bpftool_command()` and `get_bpftool_command_output()`.

Control flow: first command triggers path detection and cache fill. Commands without output redirect stdout/stderr to `/dev/null`; commands with output read up to caller-provided buffer length.

State and persistence: static `bpftool_path` persists for the process lifetime.

Dependencies and integration points: uses `bpf_util.h` `strscpy`, shell `popen`, environment variable override, and bpftool built in the kernel tools tree.

Risks: command construction is string-based and can be injection-prone if args are untrusted; `snprintf` return is not bounds-checked beyond local buffer; captured output may not be NUL-terminated by `fread`.

Test signals: tests should fail early with an explicit path error if bpftool is unavailable; command return status propagates from `pclose`.
