# sources/distributed-fs/ceph-client/drivers/mtd/sm_ftl.h

Purpose: private header for the SmartMedia/xD FTL implementation.

Important APIs/types/functions: `struct ftl_zone` stores lazy zone initialization state, an LBA-to-physical table, and a FIFO of free blocks. `struct sm_ftl` stores the blktrans device pointer, mutex, media geometry, CIS location and buffer, cache state, flush work/timer, CHS geometry, and sysfs attribute group. `struct chs_entry` maps media size to BIOS geometry. It declares internal helpers `sm_erase_block()`, `sm_mark_block_bad()`, and `sm_recheck_media()`.

Control flow and state: the header itself has no executable flow, but it defines the state machine used by `sm_ftl.c`: media-level state, per-zone mapping/free queues, and a single dirty block cache protected by `mutex` and flushed by work/timer.

Dependencies and integration: includes blktrans, kfifo, scheduler/completion, and MTD headers. It also defines `SM_FTL_PARTN_BITS` and debug print macros tied to the C file's `debug` symbol. Risks are structural: fields must remain coherent with allocation/free logic, cache bitmap width must match block sector count assumptions, and macros rely on a visible `debug` variable. Test signals are compile coverage, allocation/free path validation, and exercising cache/zone fields through `sm_ftl.c`.
