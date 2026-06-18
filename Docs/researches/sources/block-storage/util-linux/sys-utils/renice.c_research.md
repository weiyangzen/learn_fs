# File Research: sources/block-storage/util-linux/sys-utils/renice.c

This file implements `renice(1)`, changing nice values for processes, process groups, or users. It supports `-p`, `-g`, and `-u` selectors, numeric or named users, and three priority modes: historical absolute `-n`, POSIX-relative `-n` when `POSIXLY_CORRECT` is set, explicit `--priority`, and explicit `--relative`.

For each target, `donice()` reads the old priority with `getpriority()`, computes the new priority, calls `setpriority()`, reads the result back, and prints old/new values. Errors are accumulated so multiple targets can be attempted before returning failure.
