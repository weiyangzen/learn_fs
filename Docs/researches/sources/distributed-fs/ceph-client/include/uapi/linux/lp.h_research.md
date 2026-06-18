# sources/distributed-fs/ceph-client/include/uapi/linux/lp.h

Purpose: defines the legacy parallel-printer `/dev/lp*` userspace ABI: status flags, 8255 status bits, default timing constants, and printer ioctl numbers.

Important APIs and types: status flags include `LP_EXIST`, `LP_SELEC`, `LP_BUSY`, `LP_OFFL`, `LP_NOPA`, `LP_ERR`, `LP_ABORT`, `LP_ABORTOPEN`, `LP_NO_REVERSE`, and `LP_DATA_AVAIL`. Hardware status bits include `LP_PBUSY`, `LP_PACK`, `LP_POUTPA`, `LP_PSELECD`, and `LP_PERRORP`. Timing constants include `LP_INIT_CHAR`, `LP_INIT_WAIT`, `LP_INIT_TIME`, `LP_TIMEOUT_INTERRUPT`, and `LP_TIMEOUT_POLLED`. Ioctls include `LPCHAR`, `LPTIME`, `LPABORT`, IRQ get/set, `LPWAIT`, `LPABORTOPEN`, `LPGETSTATUS`, `LPRESET`, `LPGETFLAGS`, and `LPSETTIMEOUT`.

Control flow: userspace configures retry/abort, timing, IRQ/polling, and timeout behavior, writes print data, reads status, and can reset the printer. Some controls are obsolete but kept for ABI compatibility.

State and persistence: state is per printer device in the lp/parport driver: flags, timing settings, IRQ mode, and status cache. No persistent state is defined.

Dependencies and integration points: depends on `linux/types.h`, `linux/ioctl.h`, `HZ`, and word-size/time_t conditionals. Integrates the lp character device, parport, legacy tunelp tooling, and hardware status lines.

Risks and test signals: risks include old/new timeout ioctl selection on 32-bit time64 userspace, obsolete flag semantics, active-low/active-high status interpretation, and IRQ vs polling behavior. Test ioctl compatibility on 32/64-bit, status reading, timeout configuration, abort-open behavior, reset, and parport error handling.
