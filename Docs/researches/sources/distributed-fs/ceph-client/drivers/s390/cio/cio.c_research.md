# sources/distributed-fs/ceph-client/drivers/s390/cio/cio.c

## Purpose
This file implements the low-level s390 common I/O instruction wrappers and interrupt entry point for subchannels. It starts, resumes, halts, clears, cancels, configures, enables/disables, and interrogates subchannels, handles I/O interrupts, and supports early CCW console subchannels.

## Important APIs, Types, and Functions
Exports include debug identifiers, per-CPU `cio_irb`, `cio_set_options()`, `cio_start_key()`, `cio_start()`, `cio_resume()`, `cio_halt()`, `cio_clear()`, `cio_cancel()`, `cio_cancel_halt_clear()`, `cio_commit_config()`, `cio_update_schib()`, `cio_enable_subchannel()`, `cio_disable_subchannel()`, `init_cio_interrupts()`, console helpers when enabled, `cio_tm_start_key()`, and `cio_tm_intrg()`. It uses low-level I/O instructions from `ioasm.h`: `ssch`, `rsch`, `hsch`, `csch`, `xsch`, `stsch`, `msch`, and `tsch`.

## Control Flow
`cio_debug_init()` creates CIO message/trace/CRW debug areas early. Start paths build command-mode or transport-mode ORBs with interrupt parameters pointing back to the subchannel, issue `ssch`, and translate condition codes. Halt/clear/cancel/resume wrappers issue the corresponding instruction and update pending bits. `cio_cancel_halt_clear()` is a staged teardown sequence: cancel once if possible, halt up to three times, then clear up to 255 times, returning `-EBUSY` while asynchronous completion is expected. Configuration flows update a local SCHIB, call `msch`, verify the hardware accepted the target config, and retry status-pending/busy cases. `do_cio_interrupt()` reads the TPI info, `tsch()`s the IRB, updates SCSW, and dispatches to the bound CSS driver IRQ callback.

## State and Persistence
State is volatile per-subchannel SCHIB/config/ORB data and per-CPU IRBs. `cio_commit_config()` copies successful hardware state into `sch->schib`. Console support stores an early `console_sch` pointer and configures the console ISC. Hardware subchannel state persists until reconfigured by another instruction or reset, but the file itself has no disk persistence.

## Dependencies and Integration Points
It depends on architecture I/O instructions, interrupt setup, IRQ statistics, ftrace tracepoints, airq/ISC setup, CSS subchannel objects, IO-subchannel private ORBs, channel-path status, blacklist/console configuration, and CCW/transport-mode callers. It is the lowest common execution layer for `device.c`, `chsc_sch.c`, CMF, QDIO, and CCW drivers.

## Risks and Test Signals
Risk areas include condition-code translation, stale SCHIB state after failed `stsch`/`msch`, interrupt `intparm` validity, cancel/halt/clear retry exhaustion, concurrent config changes under subchannel locks, and console paths running before full bus registration. Test signals include instruction fault injection, start/halt/clear/cancel status-pending paths, enable retry without concurrent-sense after `-EIO`, transport-mode start/interrogate, no-intparm interrupts, IRQ handler dispatch with and without drivers, and early console registration.
