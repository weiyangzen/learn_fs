# sources/distributed-fs/ceph-client/arch/um/os-Linux/internal.h

## Purpose
Collects private declarations shared inside the host-Linux UML support layer.

## Important APIs, Types, and Functions
Declares `scan_elf_aux()`, `check_tmpexec()`, thread-local `signals_enabled`, `timer_alarm_pending()`, SKAS wait helpers, and defines `IPI_SIGNAL` as `SIGRTMIN`.

## Control Flow, State, and Persistence
No control flow. The header exposes shared state contracts, especially signal-enabled state and timer pending checks.

## Dependencies and Integration Points
Included by `main.c`, `signal.c`, `time.c`, `start_up.c`, and SKAS/SMP host files. It joins otherwise separate host-side modules without exporting them as public UML APIs.

## Risks and Test Signals
Risks are declaration drift and incompatible realtime-signal choices. Test SMP builds, seccomp builds, and host signal/timer idle paths.
