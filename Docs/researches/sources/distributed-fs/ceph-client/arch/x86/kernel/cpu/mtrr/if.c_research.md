# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/mtrr/if.c

Purpose: exposes the legacy `/proc/mtrr` user interface for inspecting and modifying MTRR regions through text writes and ioctls, including compat ioctl support.

Important APIs/types/functions: provides `mtrr_attrib_to_str()` globally and, under `CONFIG_PROC_FS`, defines `mtrr_write()`, `mtrr_ioctl()`, `mtrr_open()`, `mtrr_close()`, `mtrr_seq_show()`, `mtrr_file_add()`, `mtrr_file_del()`, `mtrr_proc_ops`, and `mtrr_if_init()`. It uses `mtrr_sentry`, `mtrr_gentry`, compat variants, and `FILE_FCOUNT()` per-open reference counts.

Control flow: opening `/proc/mtrr` requires MTRR support, a get callback, and `CAP_SYS_ADMIN`. Reads iterate variable ranges and display non-empty entries with base, size, count, and type. Text writes accept `disable=N` or `base=... size=... type=...`, validate alignment, and call `mtrr_add_page()` or `mtrr_del_page()`. Ioctls copy user entries, dispatch add/set/delete/kill/get operations in byte or page units, hide entries that cannot fit in legacy field widths, and copy results back. Closing a file removes entries added through that open based on per-file counts.

State and persistence: allocates a per-open `fcount` array stored in `seq_file.private`; this controls cleanup on close. It also updates global `mtrr_usage_table[]` indirectly via core MTRR add/delete calls. No disk persistence exists.

Dependencies and integration points: depends on common MTRR APIs in `mtrr.c`, `mtrr_if`, `num_var_ranges`, procfs, seq_file, capabilities, user-copy helpers, and compat ioctl definitions. It registers at `arch_initcall`.

Risks: this is a privileged legacy ABI, so parsing and ioctl field width behavior must remain compatible. Per-file cleanup can fail if counts desynchronize. Text parsing uses simple conversion helpers and fixed `LINE_SIZE`. Incorrect overflow hiding can expose invalid legacy data for ranges above representable sizes.

Test signals: `/proc/mtrr` read formatting, text add/delete/disable, all ioctl and compat ioctl commands, close-time cleanup of incremented entries, permission failure without `CAP_SYS_ADMIN`, invalid alignment/type parsing, and systems without MTRR returning open errors.
