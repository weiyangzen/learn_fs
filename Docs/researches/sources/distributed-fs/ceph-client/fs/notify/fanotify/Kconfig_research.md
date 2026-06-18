# Research: sources/distributed-fs/ceph-client/fs/notify/fanotify/Kconfig

## Purpose

This Kconfig file exposes fanotify support and optional permission-event support.

## Important APIs, Types, and Functions

`config FANOTIFY` is a prompted boolean, defaults to `n`, selects `FSNOTIFY` and `EXPORTFS`, and describes file access notification with file descriptors. `config FANOTIFY_ACCESS_PERMISSIONS` depends on FANOTIFY, defaults `n`, and enables userspace permission decisions for access events.

## Control Flow

Enabling FANOTIFY pulls in fsnotify and exportfs support. Enabling permission checking adds support for access-decision events used by scanners or storage managers.

## State and Persistence Behavior

Only kernel configuration state is affected. Runtime state is implemented in fanotify source files.

## Dependencies and Integration Points

The `EXPORTFS` select matters because fanotify can report file handles/FIDs. The permission option gates code paths that wait for userspace responses.

## Risks

Permission events expand the ability of userspace listeners to block file access and therefore have security and availability implications. Misconfigured dependencies would break FID reporting.

## Test Signals

Build with FANOTIFY off/on and with permissions off/on, confirm fsnotify/exportfs selections, and run fanotify permission-event tests only when the permission option is enabled.
