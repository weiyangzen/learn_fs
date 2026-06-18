# sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/mount-notify/Makefile

## Purpose

This Makefile builds fanotify mount notification selftests.

## Important APIs, Types, and Functions

It sets warning, optimization, debug, and kernel header CFLAGS. `TEST_GEN_PROGS := mount-notify_test mount-notify_test_ns` declares the normal and user-namespace variants. It includes `../../lib.mk`.

## Control Flow, State, and Persistence

There is no runtime flow. The Makefile registers two generated kselftest binaries.

## Dependencies, Integration Points, Risks, and Test Signals

It depends on kernel headers with fanotify mount notification definitions and kselftest build rules. It integrates both namespace variants into the filesystems selftests. Risks are header drift for newer `FAN_REPORT_MNT` and `FAN_MNT_*` constants. Passing signals are successful compilation of both test binaries.
