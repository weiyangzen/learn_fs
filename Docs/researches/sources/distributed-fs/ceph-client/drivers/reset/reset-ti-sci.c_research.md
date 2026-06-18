# sources/distributed-fs/ceph-client/drivers/reset/reset-ti-sci.c

Purpose: TI System Control Interface reset controller that maps two-cell DT reset specifiers to TI SCI device reset masks.

Important APIs/types/functions: `ti_sci_reset_control` stores `dev_id`, `reset_mask`, and a mutex for read-modify-write. `ti_sci_reset_set()` reads device reset state via TI SCI, modifies the mask, and writes it back. `ti_sci_reset_of_xlate()` allocates a control per reset spec and stores it in an IDR. Probe obtains the TI SCI handle and registers a dynamic reset provider.

Control flow: consumers with `<dev_id reset_mask>` specifiers trigger `of_xlate`, which allocates an ID. Assert/deassert/status look up the IDR entry and call TI SCI device ops.

State and persistence: IDR mappings persist for the device lifetime and are destroyed on remove. Actual reset state is maintained by system firmware.

Dependencies and integration: depends on TI SCI protocol handle, OF reset cells, IDR, mutexes, and reset-controller framework.

Risks and test signals: every unique spec allocates device-managed memory and an IDR entry; repeated translations can grow until remove. Test duplicate spec handling, concurrent set mutex behavior, SCI error propagation, remove cleanup, and malformed reset cells.
