# Research: sources/distributed-fs/ceph-client/fs/notify/dnotify/Kconfig

## Purpose

This file exposes the legacy dnotify backend configuration option.

## Important APIs, Types, and Functions

`config DNOTIFY` is a prompted boolean, defaults to `y`, and selects `FSNOTIFY`. The help text describes directory-based per-file-descriptor notifications delivered via signals and notes that newer alternatives exist.

## Control Flow

Selecting DNOTIFY enables the common fsnotify core through `select FSNOTIFY` and lets the dnotify Makefile build `dnotify.o`.

## State and Persistence Behavior

Only kernel configuration state is affected. Runtime behavior is in `dnotify.c`.

## Dependencies and Integration Points

It integrates legacy userspace ABI support with the fsnotify core. The option is user-visible and defaults on for compatibility.

## Risks

Default-on legacy support increases attack surface unless distributions choose to disable it. Removing `select FSNOTIFY` would break the build or runtime integration.

## Test Signals

Generate configs with DNOTIFY enabled/disabled, confirm `CONFIG_FSNOTIFY` follows, and confirm `dnotify.o` is built only when enabled.
