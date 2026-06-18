# sources/distributed-fs/ceph-client/drivers/s390/char/tape_proc.c

Purpose: optional procfs reporting for tape devices through `/proc/tapedevices`.

Important APIs/types/functions: defines `tape_proc_show`, seq iteration callbacks, `tape_proc_seq`, `tape_proc_init`, and `tape_proc_cleanup`.

Control flow: the seq iterator walks possible tape device indexes up to `256 / TAPE_MINORS_PER_DEV`; each row uses `tape_find_device`, locks the ccw device, prints bus id, CU/device type/model, block size, tape state, current queued operation, and medium state, then drops the device reference.

State and persistence: keeps only the proc entry pointer. Output reflects live tape state and no data is persisted.

Dependencies and integration: compiled under `CONFIG_PROC_FS`; depends on tape core device lookup, state/op verbose tables, ccw device fields, and seq_file/proc APIs.

Risks: proc output is best-effort and skips missing indexes; it must hold the ccw lock while peeking at request queue state; medium-state enum indexing assumes valid values from core/discipline.

Test signals: presence/removal of `/proc/tapedevices`, output with no devices, output with one or more online tapes, state/op changes during active I/O, and cleanup during module unload.
