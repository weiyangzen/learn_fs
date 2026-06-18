# sources/distributed-fs/ceph-client/drivers/scsi/mpi3mr/mpi3mr_debug.h

Purpose: provides driver logging level bits, unconditional controller-prefixed log macros, conditional debug-category macros, and inline helpers to dump message frames or arbitrary buffers as little-endian dwords.

Important APIs/types/functions: debug masks include event top/bottom half, init, exit, task management, reset, SCSI error/info, reply, config error/info, transport error/info, BSG error/info, generic debug, and SGE debug. Logging macros include `ioc_err`, `ioc_notice`, `ioc_warn`, `ioc_info`, category-specific `dprint_*` macros, `dprint_scsi_command()`, `dprint_dump()`, and `dprint_dump_req()`.

Control flow: normal macros format through `pr_*` with `ioc->name`. Conditional macros check `ioc->logging_level` bitmasks before printing. Dump helpers iterate over 32-bit little-endian words and print eight words per line.

State and persistence behavior: no persistent state is defined here. Runtime behavior depends on each controller's `mrioc->logging_level`, which is exposed through a writable sysfs attribute in `mpi3mr_app.c`. Log output goes to the kernel log.

Dependencies and integration points: included by `mpi3mr.h` and used throughout firmware, OS, app, config, transport, reset, and SCSI paths. `dprint_dump()` is used by BSG timeout/debug paths to show admin frames and management payloads.

Risks and test signals: risks include log flooding when verbose bits are enabled, leaking command payload contents into kernel logs, and dereferencing an invalid `ioc` in macros. Dump helpers assume dword-sized buffers and do not validate alignment beyond casting. Tests should cover compile-time macro use across modules, sysfs logging-level changes, dynamic debug scenarios for BSG timeouts, and avoiding dumps of uninitialized memory.
