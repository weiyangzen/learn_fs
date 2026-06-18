# sources/distributed-fs/ceph-client/drivers/scsi/aacraid/rkt.c

Purpose: provides the Rocket/Drawbridge variant miniport shim for RX-based AAC controllers. It mainly supplies a simple BAR mapping implementation and caps message-mode command depth to the hardware limit.

Important APIs/types/functions: `AAC_NUM_IO_FIB_RKT` defines the Rocket I/O FIB limit, `aac_rkt_select_comm()` wraps `aac_rx_select_comm()` and adjusts `can_queue` plus `init->r7.max_io_commands`, `aac_rkt_ioremap()` maps/unmaps `struct rkt_registers`, and `aac_rkt_init()` installs operations before calling `_aac_rx_init()`.

Control flow: probe enters `aac_rkt_init()`, which sets `adapter_ioremap` and `adapter_comm`, then uses the common RX initialization sequence. When firmware communication mode is selected, `aac_rkt_select_comm()` delegates to RX and, for `AAC_COMM_MESSAGE`, clamps `scsi_host_ptr->can_queue` to `246 - AAC_NUM_MGT_FIB` if the negotiated or overridden value is too high.

State and persistence: persistent driver state is only the mapped register pointer (`dev->regs.rkt`/`dev->base`), `IndexRegs`, and potentially reduced SCSI queue depth and init-struct command count. FIB and hardware communication state remain in common RX/commsup structures.

Dependencies and integration: depends on `_aac_rx_init()` and `aac_rx_select_comm()` from `rx.c`, the adapter init structure allocated by common init code, and SCSI host queue-depth fields consumed by `linit.c`.

Risks and test signals: the command-depth adjustment happens after FIB setup has already occurred according to the comment, so it limits future OS submissions but cannot resize already allocated resources. A hard-coded FIB override or firmware misreport can still stress assumptions around pool size versus hardware capacity. Test producer and message communication modes, queue clamp when `can_queue` exceeds the Rocket limit, no clamp below the limit, BAR map/unmap, and error unwind after `_aac_rx_init()` failure.
