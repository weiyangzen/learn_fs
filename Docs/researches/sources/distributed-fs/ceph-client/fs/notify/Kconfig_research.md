# Research: sources/distributed-fs/ceph-client/fs/notify/Kconfig

## Purpose

This Kconfig file defines the top-level `FSNOTIFY` symbol and includes the dnotify, inotify, and fanotify configuration submenus.

## Important APIs, Types, and Functions

`config FSNOTIFY` is a non-prompted boolean with `def_bool n`. The file then sources `fs/notify/dnotify/Kconfig`, `fs/notify/inotify/Kconfig`, and `fs/notify/fanotify/Kconfig`.

## Control Flow

Kconfig evaluation starts with a disabled internal `FSNOTIFY` symbol. Subsystems such as DNOTIFY or FANOTIFY select it when enabled.

## State and Persistence Behavior

The only persistent output is kernel configuration state. No runtime code is present.

## Dependencies and Integration Points

This file is the build-configuration integration point for filesystem notification support. It controls whether common fsnotify objects from the sibling Makefile are compiled.

## Risks

Because `FSNOTIFY` has no user prompt and defaults off, notification backends must remember to `select FSNOTIFY`. Missing a sourced submenu would silently hide a backend.

## Test Signals

Run Kconfig/config generation with DNOTIFY, INOTIFY, and FANOTIFY toggles, confirm enabling each selects `FSNOTIFY`, and confirm disabling all leaves common fsnotify code out.
