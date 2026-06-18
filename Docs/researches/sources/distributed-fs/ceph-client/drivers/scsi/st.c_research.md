## sources/distributed-fs/ceph-client/drivers/scsi/st.c

### Purpose
Implements the Linux SCSI tape character driver. It probes `TYPE_TAPE` devices, creates auto-rewind and non-rewind character devices for several modes, performs tape reads/writes with buffered or direct I/O, handles filemarks/EOM/EOD/ILI sense conditions, exposes MTIO ioctl operations, manages tape positioning/partitioning/compression/default options, and publishes sysfs configuration/statistics.

### Important APIs and Functions
- `st_template` registers the SCSI driver. `init_st()` registers the `scsi_tape` class, SCSI tape char major, and SCSI driver; `exit_st()` unregisters them.
- `st_probe()` rejects incompatible OnStream devices, allocates `struct scsi_tape`, `struct st_buffer`, stats, IDR index, mode definitions, partition state, cdevs, and sysfs devices.
- `st_open()`, `st_flush()`, and `st_release()` serialize exclusive access, runtime PM, readiness checks, buffer flush, write filemarks, optional rewind, door unlock, and reference release.
- `st_read()` and `read_tape()` handle read buffering, direct I/O mapping, READ_6 generation, read-ahead, filemark/EOM/EOD/ILI sense processing, and user copies.
- `st_write()` handles fixed/variable block writes, direct I/O, buffered writes, asynchronous write-behind, EOM retry behavior, and position accounting.
- `st_do_scsi()`, `st_scsi_execute()`, `st_scsi_execute_end()`, `st_chk_result()`, and `st_analyze_sense()` are the internal SCSI request pipeline and sense/status normalization.
- `st_ioctl()`, `st_common_ioctl()`, `st_int_ioctl()`, `get_location()`, `set_location()`, `partition_tape()`, and `st_compression()` implement MTIO operations, generic SCSI ioctl pass-through, positioning, partitioning, load/unload, erase, density/block-size/drive-buffer changes, and compression mode page updates.
- Buffer helpers `new_tape_buffer()`, `enlarge_buffer()`, `normalize_buffer()`, `clear_buffer()`, `append_to_buffer()`, `from_buffer()`, `move_buffer_data()`, `sgl_map_user_pages()`, and `sgl_unmap_user_pages()` manage reserved pages and pinned user pages.

### Control Flow and State
Probe initializes conservative defaults, mode zero, partition state, request timeouts, direct-I/O preference, and character devices for each mode/rewind combination. Open obtains the tape by IDR, enforces single opener with `st_use_lock`, resumes runtime PM, allocates a minimum buffer, and calls `check_tape()`. `check_tape()` issues TEST_UNIT_READY, handles new media and readiness, reads block limits and MODE_SENSE, sets block size/density/write protection, and applies mode defaults. Read/write calls take `STp->lock`, run common checks, optionally switch partitions, set up direct or buffered I/O, and execute READ_6/WRITE_6 through the block request path. Close flushes writes, writes filemarks according to mode, handles SysV/BSD EOF positioning, switches partitions if requested, and rewinds auto-rewind devices.

### State and Persistence Behavior
Persistent state is almost entirely in `struct scsi_tape`: mode definitions, partition status, EOF/EOM/EOD state, current and requested partition, block size, density, buffering flags, write protection, cleaning request, door lock, reset-position state, media counters, and statistics. `struct st_buffer` holds buffered data, read pointer, async write request, direct-I/O mappings, reserved pages, and command status. Some defaults are module or boot parameters (`buffer_kbs`, `max_sg_segs`, `try_direct_io`, `debug_flag`, `try_rdio`, `try_wdio`). Sysfs reports mode defaults/options and atomic counters.

### Dependencies and Integration Points
The file integrates Linux character devices, sysfs classes, IDR, kref, runtime PM, SCSI midlayer, blk-mq request execution, user-page pinning, MTIO UAPI helpers, and generic SCSI ioctl pass-through. It depends on `st.h` for state definitions and `st_options.h` for compile-time defaults.

### Risks and Test Signals
Major risks are state-machine regressions around filemarks and EOM, async write completion lifetime, direct-I/O page pin/unpin correctness, reset handling via `pos_unknown`, partition switching, MODE_SELECT page-format fallback, and single-open/reference races. Tests should cover blocking and nonblocking open with no media, read/write fixed and variable block modes, filemark write/read semantics, auto-rewind and non-rewind close behavior, EOM early warning with partial writes, ILI residual handling, MTIOCPOS/MTIOCGET/MTIOCTOP operations, partition creation/switching, compression toggles, direct-I/O fallback on alignment or mapping failure, sysfs stats, probe/remove while references exist, and error injection for SCSI sense keys.
