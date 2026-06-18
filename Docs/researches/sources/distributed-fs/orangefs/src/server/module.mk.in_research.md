# sources/distributed-fs/orangefs/src/server/module.mk.in

## Purpose
Defines the Autotools make fragment for building OrangeFS server sources when `BUILD_SERVER` is enabled. It enumerates generated state-machine C files, manually maintained server support files, server binary sources, special include flags, and optional backtrace/security certificate additions.

## Important APIs, Types, And Functions
The fragment sets `DIR := src/server`, builds `SERVER_SMCGEN` with many generated `.c` files such as `create.c`, `lookup.c`, `io.c`, `small-io.c`, `mgmt-create-root-dir.c`, and `mgmt-split-dirent.c`, appends those files to `SERVERSRC`, adds `check.c` and `config-utils.c`, tracks generated files through `SMCGEN`, and adds `pvfs2-server.c` plus `pvfs2-server-req.c` to `SERVERBINSRC`. Conditional blocks use `BUILD_SERVER`, `ENABLE_SECURITY_CERT`, and `PVFS2_SEGV_BACKTRACE`.

## Control Flow
At configure/make time, the surrounding build system substitutes `@BUILD_SERVER@` and `@PVFS2_SEGV_BACKTRACE@`. If server builds are enabled, this fragment contributes generated state-machine files to the server library, links daemon-only files separately, optionally includes `mgmt-get-user-cert.c`, and applies `-D__PVFS2_SEGV_BACKTRACE__` to `pvfs2-server.c` when requested.

## State And Persistence
The file affects build state rather than runtime state. It records which generated artifacts are considered part of the server and which are cleaned during dist-clean via `SMCGEN`.

## Dependencies And Integration Points
It integrates the server directory with the top-level build system, the state-machine generator, optional certificate-security code, Trove handle-management include paths for `statfs.c`, and the backtrace code guarded in `pvfs2-server.c`. Its file list must match actual generated state machines and request-table entries.

## Risks And Test Signals
Risks include missing a generated state-machine source when a new protocol op is added, including a request-table entry whose state-machine object is not linked, stale conditional coverage for `ENABLE_SECURITY_CERT`, and dist-clean missing generated files. Test signals include full server builds with and without `BUILD_SERVER`, certificate support, and segv backtrace; clean/distclean runs; and link checks that all `pvfs2_*_params` references in `pvfs2-server-req.c` resolve.
