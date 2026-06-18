# sources/distributed-fs/ceph-client/drivers/scsi/be2iscsi/be.h

Purpose: provides core BladeEngine iSCSI controller data structures and helper primitives shared by BE2 iSCSI command, management, and main driver code.

Important APIs/types/functions: `struct be_dma_mem` describes DMA allocations. `struct be_queue_info` models firmware rings with DMA memory, length, entry size, id, head/tail, creation flag, and used count. Queue helpers include `MODULO()`, `index_inc()`, `queue_head_node()`, `queue_tail_node()`, `queue_get_wrb()`, and head/tail increment wrappers. `struct be_eq_obj`, `struct be_mcc_obj`, `struct beiscsi_mcc_tag_state`, and `struct be_ctrl_info` hold event queues, MCC queues, mailbox DMA memory, locks, wait queues, and MCC tag bookkeeping. AMAP helpers set/get packed firmware bitfields, and `swap_dws()` handles big-endian dword conversion.

Control flow: this header supplies inline mechanics used whenever code allocates a WRB, advances a queue, waits on a mailbox tag, or fills firmware bitfield contexts. `be_cmds.c` uses `be_ctrl_info` for mailbox/MCC serialization and `be_queue_info` for ring creation and command submission.

State and persistence: controller state is volatile and tied to a PCI function. Mailbox memory, MCC queue state, tag arrays, tag status, and tag wait queues live in `be_ctrl_info` for the lifetime of the HBA. Firmware-assigned queue IDs are cached in `be_queue_info.created/id`.

Dependencies and integration: includes PCI, VLAN, and IRQ polling headers, then includes `be_cmds.h`, making command structures part of the shared controller contract. It integrates tightly with `be_main.h` for `struct beiscsi_hba` and with firmware queue formats in `be_cmds.h`.

Risks and test signals: `MODULO()` assumes power-of-two queue lengths and warns otherwise; all ring lengths must satisfy that. Pointer arithmetic on `void *` relies on GNU C kernel conventions. MCC tag state uses bit flags and DMA memory retention for timeout cleanup, so races between timeout and late completion are important. Test signals include endian builds, queue wraparound, MCC tag exhaustion/reuse, late completion cleanup, and firmware context bitfield encoding.
