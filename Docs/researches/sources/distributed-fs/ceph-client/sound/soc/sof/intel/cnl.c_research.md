# sources/distributed-fs/ceph-client/sound/soc/sof/intel/cnl.c

Purpose: `cnl.c` specializes HDA common operations for Cannonlake-class cAVS 1.8 and JasperLake cAVS 2.0 platforms, including sideband IPC register handling, IPC4 support, debug dumps, and exported chip descriptors.

Important APIs: exported functions include `cnl_ipc_irq_thread()`, `cnl_ipc4_irq_thread()`, `cnl_ipc_send_msg()`, `cnl_ipc4_send_msg()`, `cnl_ipc_dump()`, `cnl_ipc4_dump()`, `sof_cnl_ops_init()`, and exported descriptors `cnl_chip_info` and `jsl_chip_info`. Internal helpers acknowledge target and initiator IPC channels through `cnl_ipc_host_done()` and `cnl_ipc_dsp_done()`, while `cnl_compact_ipc_compress()` encodes PM_GATE IPC3 messages into compact registers.

Control flow: IPC3 and IPC4 IRQ threads read sideband HIPCI/HIPCT registers, distinguish host acknowledgements from DSP-originated messages, handle replies only after firmware boot, route notifications through SOF IPC receive paths, and handle panic magic with boot-retry awareness. Send functions write mailbox payloads when needed, write extension registers, set BUSY in the primary register, and schedule D0I3 delayed work for non-PM IPCs. IPC4 transmit defers a message in `hdev->delayed_ipc_tx_msg` when the request register is busy and retries after ACK.

State and persistence behavior: `sof_cnl_ops_init()` clones common HDA ops and mutates the global `sof_cnl_ops`. IPC4 allocation stores `struct sof_ipc4_fw_data` in `sdev->private`, including manifest offset, mtrace type, and library loading callback. Chip descriptors persist register offsets, masks, SoundWire hooks, SSP layout, ROM timeout, and power callbacks.

Dependencies, risks, and test signals: this file depends on HDA common IPC/DSP helpers, IPC4 topology headers, tracepoints, SoundWire helpers, and the code loader. Risks include sideband register ack ordering, delayed IPC lifetime, compact PM_GATE encoding, and boot-panic recoverability classification. Test IPC3 and IPC4 boot, D0I3 PM_GATE transitions, delayed IPC send under busy conditions, SoundWire IRQ/wake handling, and JasperLake using CNL ops despite ICL lineage.
