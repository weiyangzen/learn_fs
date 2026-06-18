# File Research: sources/block-storage/util-linux/sys-utils/blkpr.c

## Scope

Implements `blkpr`, a command-line frontend for Linux block persistent reservation ioctls.

## Public And Internal APIs Covered

- Main command-line entry point.
- Command parsing for `register`, `reserve`, `release`, `preempt`, `preempt-abort`, `clear`, and conditionally `read-keys` / `read-reservation`.
- Type parsing for persistent reservation access types.
- Flag parsing for `ignore-key`.
- Ioctl executor `do_pr()`.

## Control Flow And Behavior

- Static descriptor tables map user strings to kernel persistent-reservation command/type/flag constants and usage text.
- `do_pr()` opens the device read/write and dispatches by command:
  - `IOC_PR_REGISTER` uses `struct pr_registration`.
  - `IOC_PR_RESERVE` / `IOC_PR_RELEASE` use `struct pr_reservation`.
  - `IOC_PR_PREEMPT` / `IOC_PR_PREEMPT_ABORT` use `struct pr_preempt`.
  - `IOC_PR_CLEAR` uses `struct pr_clear`.
  - Optional read commands print registered keys or current reservation.
- `do_pr_read_keys()` grows the key buffer until the kernel-reported key count fits.
- `do_pr_read_reservation()` prints key, generation, and reservation type, or `No reservation`.

## Dependencies

- Linux persistent reservation API from `<linux/pr.h>`.
- util-linux string parsing, allocation, usage, and i18n helpers.

## Risks And Invariants

- String tables must stay aligned with kernel reservation type/command constants.
- Missing command validation is limited: `command` defaults to `-1`, and `do_pr()` handles unknown commands as `EINVAL`.
- Positive ioctl return values are treated as device-model error codes and reported separately from syscall failure.
- Optional read commands depend on kernel headers defining `IOC_PR_READ_KEYS` / `IOC_PR_READ_RESERVATION`.
