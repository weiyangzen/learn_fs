# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mthca/mthca_cmd.c

## Purpose
`mthca_cmd.c` implements the firmware command interface for mthca. It posts commands through the HCR or optional firmware command doorbell page, waits by polling or EQ command events, manages command mailboxes, maps firmware/ICM memory, queries capabilities, initializes HCA/IB ports, and wraps resource state transitions for MPT, MTT, EQ, CQ, SRQ, QP, MAD, and multicast objects.

## Important APIs, types, and functions
Core internals include `mthca_cmd_post_hcr()`, `mthca_cmd_post_dbell()`, `mthca_cmd_poll()`, `mthca_cmd_wait()`, `mthca_cmd_box()`, `mthca_cmd_imm()`, and `mthca_status_to_errno()`. Lifecycle APIs are `mthca_cmd_init()`, `mthca_cmd_use_events()`, `mthca_cmd_use_polling()`, and `mthca_cmd_cleanup()`. Mailboxes are allocated by `mthca_alloc_mailbox()`. Public wrappers include `mthca_SYS_EN/DIS`, `QUERY_FW`, `ENABLE_LAM`, `QUERY_DDR`, `QUERY_DEV_LIM`, `QUERY_ADAPTER`, `INIT_HCA`, `INIT_IB`, `SET_IB`, ICM map/unmap commands, resource `SW2HW/HW2SW` commands, `mthca_MODIFY_QP()`, `mthca_MAD_IFC()`, MGM commands, and `mthca_NOP()`.

## Control flow
Before EQ setup, callers use polling mode: post HCR, wait for GO bit to clear, read status/out parameter. After EQ setup, `mthca_cmd_use_events()` allocates token contexts and holds the polling semaphore; commands reserve a context, post with event bit, sleep for completion, and are completed by `mthca_cmd_event()` from EQ processing. Higher wrappers allocate mailboxes, encode firmware command layouts with `MTHCA_PUT`, issue the opcode, decode outputs with `MTHCA_GET`, and free mailboxes. Mapping commands batch ICM chunks into mailbox entries.

## State and persistence
Driver state includes mapped HCR, command DMA pool, HCR mutex, polling and event semaphores, token contexts, command flags, optional doorbell-page mapping, and firmware-discovered limits. Persistent device state includes firmware execution, LAM state, mapped firmware/ICM/aux memory, initialized HCA and IB ports, and hardware object ownership after SW2HW/HW2SW transitions.

## Dependencies and integration points
It depends on PCI MMIO, DMA pools, completions, semaphores, EQ command events from `mthca_eq.c`, mailbox layout macros from `mthca_dev.h`, memfree ICM helpers, RDMA MAD structures, and every table manager that needs firmware object transitions.

## Risks
Timeouts are coarse 60-second waits because firmware can be starved. Late completions are ignored by token mismatch but still imply firmware made progress after callers timed out. Event-mode teardown drains semaphores and assumes no active users remain. Doorbell command posting is optional and gated by firmware plus module parameter. Many command layouts use hard-coded offsets; mistakes silently corrupt firmware requests. `mthca_DISABLE_LAM()` calls `CMD_SYS_DIS`, which is notable because a separate `CMD_DISABLE_LAM` constant exists.

## Test signals
Exercise polling and event modes, HCR busy timeout, command event completion, late completion after timeout, status-to-errno mapping, mailbox allocation failure, firmware doorbell mapping, QUERY_FW parsing for Tavor and Arbel, ICM map batching, INIT_HCA endianness flags, QP state transition matrix, MAD_IFC with and without WC/GRH, and teardown while commands are quiesced.
