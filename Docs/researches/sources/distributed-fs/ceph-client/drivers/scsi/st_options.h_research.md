## sources/distributed-fs/ceph-client/drivers/scsi/st_options.h

### Purpose
Provides compile-time default policy for the SCSI tape driver. These macros seed module-level defaults and per-mode settings in `st.c`, while many can later be overridden through module parameters or MTSETDRVBUFFER/MT_ST_OPTIONS ioctl controls.

### Important APIs, Types, and Constants
- `TRY_DIRECT_IO`, `ST_NOWAIT`, `ST_IN_FILE_POS`, `ST_RECOVERED_WRITE_FATAL`, and `ST_DEFAULT_BLOCK` set core behavior for direct I/O, immediate commands, positioning assumptions, recovered write errors, and fallback block size.
- Buffer sizing defaults are `ST_FIXED_BUFFER_BLOCKS`, `ST_MAX_SG`, `ST_FIRST_SG`, and `ST_FIRST_ORDER`.
- Per-drive/mode defaults include `ST_TWO_FM`, `ST_BUFFER_WRITES`, `ST_ASYNC_WRITES`, `ST_READ_AHEAD`, `ST_AUTO_LOCK`, `ST_FAST_MTEOM`, `ST_SCSI2LOGICAL`, `ST_SYSV`, and `ST_SILI`.
- `ST_BLOCK_SECONDS` controls how long blocking open waits for a drive to become ready.

### Control Flow and State
The file has no executable flow. `st.c` reads these macros during module initialization, probe, and mode initialization to seed runtime fields such as `try_direct_io`, `do_async_writes`, `do_buffer_writes`, `do_read_ahead`, `two_fm`, `fast_mteom`, `sili`, and readiness wait behavior.

### Dependencies and Integration Points
This header is included only by `st.c` before `st.h`. Its values interact with module parameters (`buffer_kbs`, `max_sg_segs`, `try_direct_io`) and MTIO option ioctls that can modify per-device/per-mode behavior after probe.

### Risks and Test Signals
Default changes alter user-visible tape semantics. Tests should verify default fixed buffer size, direct-I/O attempts and fallback, async write behavior, read-ahead behavior, auto-rewind/non-rewind close behavior, no automatic door lock by default, and the 120-second blocking-open readiness policy when a drive is becoming ready.
