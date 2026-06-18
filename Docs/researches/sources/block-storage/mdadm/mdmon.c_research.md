# File Research: sources/block-storage/mdadm/mdmon.c

## Role

`mdmon.c` is the entry point for the mdmon daemon, which manages arrays with user-space external metadata. It validates the target container, loads its metadata handler, creates pid/socket control files, starts the high-priority monitor thread/process, and runs the manager loop.

## Main Flow

- Parses `--all`, `--takeover`, `--foreground`, `--offroot`, and `--help`.
- In `--all` mode, scans `/proc/mdstat` and starts mdmon for each external metadata container that is not a subarray.
- Resolves user-supplied container names to md kernel names and validates them through `open_mddev()`.
- `mdmon()` opens the container, optionally forks and reports startup status to the parent, reads sysfs metadata/version/device information, verifies the array is an external-metadata container, and maps the metadata string to a `superswitch`.
- Copies container component device info into `container->devs`, blocks `SIGUSR1`/`SIGTERM`, configures signal handlers, and checks for an existing mdmon.
- On takeover, removes old pid/socket files, creates a new pid file and nonblocking Unix-domain control socket, locks memory with `mlockall()`, starts the monitor worker with pthreads or `clone()`, then runs `do_manager()`.

## Process and IPC Behavior

- `make_pidfile()` writes `${MDMON_DIR}/${devnm}.pid`.
- `make_control_sock()` creates `${MDMON_DIR}/${devnm}.sock` with restrictive umask and nonblocking mode.
- `try_kill_monitor()` verifies an old process looks like mdmon, sends `SIGTERM`, waits for socket closure, and pokes it with `SIGUSR1` while it exits.
- The monitor side is launched either as a detached pthread or a shared address-space `clone()` thread, with shared files, filesystem context, VM, and signal handlers in clone mode.

## Special Handling

- `imsm_set_no_platform(1)` suppresses IMSM platform complaints from mdmon; mdadm proper owns user-facing platform diagnostics.
- If running from initrd, the first character of `argv[0]` is set to `@` so systemd can preserve the task during shutdown.
- Provides stub implementations for reshape/stripe helpers and native `super0`/`super1` symbols so metadata code can link in the mdmon binary.

## Invariants and Risks

- mdmon only accepts containers with external metadata: sysfs level `UnSet`, major version `-1`, minor version `-2`.
- Control paths are fixed-size buffers around `MDMON_DIR`; md device names are constrained by `MD_NAME_MAX`.
- Startup uses a parent/child pipe so foreground command execution knows whether daemon setup succeeded.
- Existing mdmon takeover is race-sensitive and relies on pidfile/socket validation plus metadata loading before replacing the old monitor.
