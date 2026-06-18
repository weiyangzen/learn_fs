# sources/distributed-fs/ceph-client/fs/coredump.c

Purpose: implements Linux VFS core dump orchestration: pattern expansion, process/thread quiescing, output target setup for files, pipe helpers, and AF_UNIX sockets, invoking binary-format dump writers, exported dump-write helpers, coredump sysctls, and VMA dump selection.

Important APIs/functions: `vfs_coredump()` is the top-level entry from fatal signal handling. `coredump_parse()` expands `core_pattern` tokens and identifies file, pipe, socket, or socket request protocol outputs. `coredump_wait()` zaps sibling threads and waits for stable state. `coredump_file()`, `coredump_pipe()`, and `coredump_socket()` set up output. `do_coredump()` drives target setup, optional rejection, file-table unshare, `binfmt->core_dump()`, and helper waiting. Exported helpers `dump_emit()`, `dump_skip_to()`, `dump_skip()`, `dump_user_range()`, and `dump_align()` are used by ELF and other binfmt dumpers.

Control flow: `vfs_coredump()` snapshots dumpability flags, optionally switches fsuid to root for suid-safe dumps, coordinates threads, then runs `do_coredump()` under scoped creds. Output setup enforces `RLIMIT_CORE`, suid path rules, pipe recursion guard, `core_pipe_limit`, or socket request/ack masks. `coredump_write()` snapshots VMAs, calls the binfmt writer, fixes trailing sparse skips, and frees snapshots. Cleanup closes files, decrements pipe counters, frees names, and wakes killed threads.

State and persistence: sysctl globals include `core_pattern`, `core_uses_pid`, `core_pipe_limit`, `core_file_note_size_limit`, and `core_sort_vma`. Per-dump state lives in `coredump_params`, `core_name`, `core_state`, and VMA metadata. Core files or userspace processing are the persistent outputs.

Dependencies/integration: integrates signals, credentials, pidfs, usermodehelper, pipes, AF_UNIX sockets, VFS file creation/security, mm/VMA iteration, binfmt core writers, sysctls, audit, tracepoints, freezer, and proc connector behavior.

Risks: security rules for suid dumps and `core_pattern` paths are critical. Socket mode requires initial mount namespace validation and dotdot/path length checks. Thread coordination must avoid races with exit/exec. Dump helpers must honor limits and interruption. VMA snapshotting uses write mmap lock due to stack expansion concerns.

Test signals: `core_pattern` token expansion, file/pipe/socket outputs, `%F` pidfd helper behavior, suid dump mode safety, `core_pipe_limit`, socket ack rejection/wait masks, interrupted dumps, sparse output via `dump_skip`, VMA filtering flags, sysctl validation, and ELF core readability.
