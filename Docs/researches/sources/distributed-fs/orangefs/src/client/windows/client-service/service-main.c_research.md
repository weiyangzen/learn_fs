# sources/distributed-fs/orangefs/src/client/windows/client-service/service-main.c

## Purpose
`service-main.c` is the executable entry point and Windows service control layer for the OrangeFS client. It can install/remove the service, run as a Windows service, or run as a console process, then starts filesystem initialization and the Dokany mount loop.

## Important APIs, Types, And Functions
Major functions include `main`, `service_main`, `service_ctrl`, `service_install`, `service_remove`, `main_init`, `main_loop`, `main_thread_start`, `main_thread_stop`, `cache_thread_start`, `cache_thread_stop`, `check_mount_point`, service/event log helpers, and error formatting/reporting helpers. Globals include service status handles, `is_running`, `run_service`, worker thread handles, `debug_log`, global caches, and global `PORANGEFS_OPTIONS goptions`.

## Control Flow
Command-line parsing handles install/remove, service mode, mount override, and debug mode. Both service and console paths initialize ETW, Winsock, OpenSSL, user and IO caches, parse config, add users, configure gossip debug variables, validate the mount point, start the user-cache maintenance thread, and call `main_loop`. `main_loop` finds `PVFS2TAB_FILE` or a tab file beside the executable, retries `fs_initialize` every 15 seconds while running, then calls `dokan_loop`. Service stop/shutdown marks pending stop and requests Dokany unmount via `DokanRemoveMountPoint`.

## State And Persistence
Persistent system state is affected by `service_install` and `service_remove` through the Windows Service Control Manager. Runtime state includes global options, cache qhashes, mutexes, service status, ETW registration, debug file `service.log`, and the mounted Dokany filesystem. Filesystem state is delegated to OrangeFS via `fs.c`.

## Dependencies And Integration Points
It depends on Dokany, Windows SCM/threading/Winsock APIs, OpenSSL, gossip, generated ETW `messages.h`, configuration, certificate, user-cache, IO-cache, and `fs.h`. It starts the `dokan_loop` defined in `dokany-interface.c`.

## Risks And Test Signals
Cleanup ordering is fragile: `service_main_exit` can free/destroy caches and call `free(options)` even if allocation/configuration failed before options is initialized in some paths. `cache_thread_stop` uses `TerminateThread`, which can interrupt while holding `user_cache_mutex` or owning OpenSSL/heap objects. `main_thread_start` waits indefinitely on the mount thread, so service startup blocks inside service_main after reporting running. The service install path does not quote executable paths with spaces. Client-test coverage validates mounted behavior after startup but not service install/remove, SCM status transitions, ETW registration, retry behavior, or shutdown cleanup.
