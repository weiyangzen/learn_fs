# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_tpc0_cfg_qm_sync_object_regs.h

Purpose: minimal generated map for QM sync-object registers in the TPC CFG block. It exports two addresses: `mmDCORE0_TPC0_CFG_QM_SYNC_OBJECT_MESSAGE` at `0x400BADC` and `mmDCORE0_TPC0_CFG_QM_SYNC_OBJECT_ADDR` at `0x400BAE0`.

Important APIs/types/functions: no functions/types. The macro pair names the message payload and target address registers used for synchronization object signaling through the TPC queue-manager configuration path.

Control flow: none locally. External command or firmware paths write the message and address in the correct hardware-defined order as part of sync-object signaling.

State and persistence behavior: describes two hardware registers whose contents define a synchronization-object write. Incorrect persisted values may signal the wrong completion object or fail to notify waiters.

Dependencies and integration points: included by `gaudi2_regs.h`; adjacent to `dcore0_tpc0_cfg_qm_regs.h` address space and conceptually linked to queue completion, fences, and sync manager blocks.

Risks: the two-register protocol is ordering-sensitive. Address/message inversion, partial programming, or stale contents can break host/device synchronization and cause hangs or premature completion.

Test signals: queue completion tests involving sync objects; MMIO write-order review; integration tests that wait on TPC QM completions; generated map validation for the two adjacent addresses.
