# sources/distributed-fs/ceph-client/arch/powerpc/kernel/rtasd.c

Purpose: RTAS event-scan daemon support. It polls firmware for platform events, logs RTAS errors to printk/NVRAM/in-memory proc buffers, exposes `/proc/powerpc/rtas/error_log`, and optionally enables surveillance heartbeat indicators.

Important APIs/types/functions: `pSeries_log_error()`, `printk_log_rtas()`, `log_rtas_len()`, `handle_rtas_event()`, `rtas_log_read()`, `rtas_log_poll()`, `enable_surveillance()`, `do_event_scan()`, delayed work `event_scan_work`, `rtas_event_scan()`, `retrieve_nvram_error_log()`, `start_event_scan()`, `rtas_cancel_event_scan()`, `rtas_event_scan_init()`, `rtas_init()`, and boot params `surveillance=` and `rtasmsgs=`.

Control flow: `arch_initcall(rtas_event_scan_init)` checks platform and `event-scan` token, reads `rtas-event-scan-rate`, allocates a circular vmalloc log buffer, retrieves any saved NVRAM error, then schedules delayed scanning. `do_event_scan()` repeatedly calls RTAS `event-scan` with `RTAS_EVENT_SCAN_ALL_EVENTS` until no more events; ordinary events are logged via `pSeries_log_error()`, while PRRN is rate-limited/ignored by this file. The delayed work rotates across online CPUs, adjusts the initial delay after the first pass, and enables surveillance if configured. The proc reader blocks until a circular-buffer record exists, copies one fixed-size record to userspace, and clears NVRAM when it has caught up.

State and persistence: in-memory ring state is `rtas_log_buf`, `rtas_log_start`, `rtas_log_size`, and `error_log_cnt` under `rtasd_log_lock`. On PPC64, non-boot nonfatal errors are also written to NVRAM and recovered on next boot, with logging disabled after fatal errors. `full_rtas_msgs` changes printk verbosity.

Dependencies and integration points: depends on RTAS core token/call/error-log-size APIs, pSeries/CHRP machine detection, NVRAM error-log helpers, workqueues, CPU topology, procfs, and platform `ppc_md.log_error` users. `rtas_flash.c` calls `rtas_cancel_event_scan()` before firmware update.

Risks: event scanning depends on firmware rate values; rate zero disables scanning and missing properties disable the daemon. The log buffer uses fixed-size records with sequence number plus firmware-sized payload, so reader count must be at least `rtas_error_log_buffer_max`. Locking spans NVRAM/log buffer operations; fatal paths disable logging permanently. Polling too quickly is explicitly avoided because some machines misbehave.

Test signals: boot pSeries/CHRP with event-scan token, verify daemon start, proc entry creation, blocking/nonblocking reads, NVRAM recovery/clear behavior, `rtasmsgs=1` full dumps, injected RTAS events, surveillance boot param, CPU hotplug work rescheduling, and flash module cancellation.
