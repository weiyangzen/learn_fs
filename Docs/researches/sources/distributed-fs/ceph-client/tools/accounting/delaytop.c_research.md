# sources/distributed-fs/ceph-client/tools/accounting/delaytop.c

## Purpose
Provides a top-like userspace monitor for system pressure, cgroup statistics, and per-task delay accounting. It samples PSI from `/proc/pressure`, fetches taskstats over generic netlink, sorts tasks by selected delay metric, and supports interactive key handling.

## Important APIs, Types, And Functions
- `struct psi_stats`, `task_info`, `container_stats`, `field_desc`, and `config` hold sampled data and UI/settings state.
- Netlink helpers `create_nl_socket()`, `send_cmd()`, and `get_family_id()` access the `TASKSTATS` generic netlink family.
- `read_psi_stats()` parses CPU/memory/IO/IRQ PSI files.
- `fetch_and_fill_task_info()` requests `TASKSTATS_CMD_ATTR_PID` and copies delay fields into `tasks[]`.
- `get_task_delays()` scans `/proc` or one PID and fills up to `MAX_TASKS`.
- `get_container_stats()` sends `CGROUPSTATS_CMD_GET` for a cgroup path.
- `compare_tasks()` sorts by average delay using configured field offsets.
- `display_results()`, `check_for_keypress()`, and `handle_keypress()` implement terminal output and interactive mode switching/sorting.

## Control Flow
`main()` parses options, opens a generic netlink socket, discovers the taskstats family id, puts the terminal in raw mode, and loops until iteration count, one-shot mode, or quit. Each iteration verifies display mode/sort compatibility, reads PSI, optionally reads cgroup stats, fetches task delay stats, sorts the global task array, renders the screen, waits for keyboard input with `select()`, and handles mode/sort/quit commands.

## State And Persistence
State is process-local globals: current config, PSI sample, task array, task count, running flag, container stats, netlink socket, family id, and terminal mode. There is no file persistence. It temporarily changes terminal settings and restores them on normal exit.

## Dependencies And Integration Points
Depends on Linux generic netlink, `linux/taskstats.h`, `linux/cgroupstats.h`, `/proc`, `/proc/pressure/*`, and terminal APIs. It integrates with kernel delay accounting and PSI facilities; meaningful data requires kernel support and permissions to query taskstats.

## Risks
- `enable_raw_mode()` lacks signal/atexit restoration, so abnormal termination can leave terminal settings changed.
- `compare_tasks()` reads count fields as `unsigned long` even fields are `unsigned long long`, which can truncate on 32-bit builds.
- Per-PID netlink queries while scanning `/proc` can race with process exit and print many transient errors.
- `get_container_stats()` passes `&cfd` with `sizeof(__u32)`; this relies on fd size matching u32 representation.
- `read_psi_stats()` returns warning counts as truthy; UI prints "PSI not found" for any warning, not just missing PSI.

## Test Signals
Run `delaytop -o`, `-p <pid>`, `-M`, `-s` for every field, `-C <cgroup>`, and interactive `o/M/q`. Test with PSI disabled, taskstats unavailable, rapidly exiting tasks, non-TTY stdin, and 32-bit builds if supported.
