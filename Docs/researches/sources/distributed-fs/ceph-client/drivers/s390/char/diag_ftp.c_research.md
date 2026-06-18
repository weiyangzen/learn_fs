# sources/distributed-fs/ceph-client/drivers/s390/char/diag_ftp.c

Purpose: implements the z/VM DIAGNOSE X'2C4' backend for HMC FTP services used by `hmcdrv`.

Important APIs/types/functions: `struct diag_ftp_ldfpl` is the load-file parameter list; `diag_ftp_handler()` handles external service interrupts; `diag_ftp_2c4()` issues the inline `diag` instruction; `diag_ftp_cmd()` prepares a DMA page, starts the async transfer, waits for completion, and maps status codes; `diag_ftp_startup()`/`shutdown()` register interrupt handling and service-signal subclass.

Control flow: callers serialize access externally. A command allocates an aligned DMA LDFPL, copies the HMC file identifier, fills buffer real address, length, and offset, issues DIAG X'2C4', then waits unconditionally for the external interrupt because cancellation is unavailable. Completion status determines byte count or errno.

State and persistence behavior: global completion and `diag_ftp_subcode` are transient backend state. File transfers affect remote HMC media according to the command, not local persistent kernel state.

Dependencies and integration points: used by `hmcdrv_ftp.c` on z/VM; depends on s390 diag instruction support, external IRQ registration, service-signal subclass, DMA-addressable pages, and HMC FTP command specs.

Risks and test signals: non-reentrant globals require caller mutexing; a lost interrupt would block forever; filename length and DMA alignment are critical. Test startup/shutdown, busy/permission/I/O/status mappings, invalid long names, zero-length transfers, and concurrent caller exclusion through `hmcdrv_ftp`.
