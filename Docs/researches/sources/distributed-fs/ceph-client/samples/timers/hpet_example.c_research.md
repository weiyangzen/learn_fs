# sources/distributed-fs/ceph-client/samples/timers/hpet_example.c

## Purpose

This user-space sample exercises HPET character device operations: open/close, query info, polling periodic interrupts, and asynchronous SIGIO notification.

## Important APIs, Types, and Functions

The command table dispatches to `hpet_open_close()`, `hpet_info()`, `hpet_poll()`, and `hpet_fasync()`. It uses `open`, `close`, HPET ioctls `HPET_INFO`, `HPET_IRQFREQ`, `HPET_EPI`, `HPET_IE_ON`, `poll`, `read`, `fcntl(F_SETOWN/F_GETFL/F_SETFL|O_ASYNC)`, `signal(SIGIO)`, `pause`, and `gettimeofday`.

## Control Flow

`main()` removes the program name, looks up the first argument in the command table, and calls the matching handler. `open-close` only validates open. `info` prints `struct hpet_info`. `poll` configures interrupt frequency, enables periodic mode when supported, enables interrupts, then polls and reads expiration counts for the requested iterations. `fasync` installs a SIGIO handler, configures async ownership and frequency, enables interrupts, and waits for signals.

## State and Persistence Behavior

Runtime state is the HPET fd configuration, process signal handler, and global `hpet_sigio_count`. Device interrupt settings are active while fd is open.

## Dependencies and Integration Points

It depends on `/dev/hpet` or another HPET device path, HPET UAPI headers, and kernel HPET support.

## Risks and Edge Cases

The code checks some `fcntl` calls against `== 1`, which is unusual because errors are `-1`; this may miss failures. Frequency and iteration parsing uses `atoi` without validation. Poll and signal loops can block indefinitely.

## Test Signals

Run `hpet_example info /dev/hpet`, then `poll /dev/hpet <freq> <iterations>` and `fasync /dev/hpet <freq> <iterations>` on HPET-capable hardware.
