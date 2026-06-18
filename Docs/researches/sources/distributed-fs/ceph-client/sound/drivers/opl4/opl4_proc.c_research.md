# sources/distributed-fs/ceph-client/sound/drivers/opl4/opl4_proc.c

## Purpose
Exposes OPL4 memory through an ALSA proc binary entry named `opl4-mem`. On classic OPL4 it allows read/write access to external ROM/SRAM space; on OPL4-ML it exposes read-only-size semantics for internal ROM.

## Important APIs, Types, And Functions
`snd_opl4_create_proc()` creates the proc entry, sets size and content type, and assigns `snd_opl4_mem_proc_ops`. `snd_opl4_mem_proc_open()` and release serialize access with `memory_access`; read/write handlers allocate temporary buffers, copy to/from user, and call `snd_opl4_read_memory()` or `snd_opl4_write_memory()`. `snd_opl4_free_proc()` removes the entry.

## Control Flow
Open takes `access_mutex` and rejects concurrent access with `-EBUSY`. Read allocates a kernel buffer of requested count, reads device memory at the file offset, copies it to user space, and frees the buffer. Write copies user bytes into a temporary buffer, writes them to device memory, and frees it.

## State And Persistence
Runtime state includes the proc entry pointer and `memory_access` count. The only persistent-like state is actual OPL4 external memory if writable hardware is present; the driver does not validate memory content.

## Dependencies And Integration
Depends on `CONFIG_SND_PROC_FS`, ALSA info/proc APIs, vmalloc/vfree, user copy helpers, and OPL4 memory helpers.

## Risks And Test Signals
Large reads/writes vmalloc the full request size and do not clamp offsets/counts against entry size in the file code itself. Write access to external SRAM can alter hardware memory. Tests should cover concurrent open rejection, read/write at boundary offsets, OPL4 versus OPL4-ML entry sizing and mode bits, and cleanup on device removal.
