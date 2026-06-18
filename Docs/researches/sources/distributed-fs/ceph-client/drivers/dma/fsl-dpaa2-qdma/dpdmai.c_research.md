# sources/distributed-fs/ceph-client/drivers/dma/fsl-dpaa2-qdma/dpdmai.c Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/fsl-dpaa2-qdma/dpdmai.c -->
## sources/distributed-fs/ceph-client/drivers/dma/fsl-dpaa2-qdma/dpdmai.c

### Purpose
`dpdmai.c` is a thin Management Complex command wrapper for DPAA2 Data Path DMA Interface objects. It opens, closes, enables, disables, resets, destroys, queries attributes, and configures or queries DPDMAI RX/TX queues for the QDMA driver.

### Important APIs, Types, And Functions
Exported APIs are `dpdmai_open()`, `dpdmai_close()`, `dpdmai_destroy()`, `dpdmai_enable()`, `dpdmai_disable()`, `dpdmai_reset()`, `dpdmai_get_attributes()`, `dpdmai_set_rx_queue()`, `dpdmai_get_rx_queue()`, and `dpdmai_get_tx_queue()`. Internal packed command/response layouts include `struct dpdmai_cmd_open`, `struct dpdmai_cmd_destroy`, `struct dpdmai_rsp_get_attributes`, `struct dpdmai_cmd_queue`, and `struct dpdmai_rsp_get_tx_queue`.

### Control Flow, State, And Persistence
Each function creates a zeroed `struct fsl_mc_command`, encodes the command header with the relevant command ID and token, writes little-endian command parameters into `cmd.params`, calls `mc_send_command()`, and decodes returned parameters on success. `dpdmai_open()` returns the MC token stored in the response header; all later calls use that token to authenticate the DPDMAI session. Queue setters pass destination type, destination ID, priority, user context, options, queue index, and priority selection to the MC firmware. Queue getters decode FQIDs and destination attributes for use by enqueue/dequeue paths.

### Dependencies, Integration Points, Risks, And Test Signals
The file depends on `linux/fsl/mc.h`, MC command header helpers, endian conversion, and public structures from `dpdmai.h`. It integrates directly with `dpaa2-qdma.c` probe, bind, enable, notification routing, reset, and shutdown. Risks include packed layout drift against MC firmware ABI, incorrect queue/priority union use, versioned command IDs for queue operations, and `DEST_TYPE_MASK` truncation if firmware expands destination encoding. Test signals include MC command success/failure injection, token lifecycle, attribute version decoding, RX queue destination programming, TX/RX FQID retrieval, and endian correctness on big- and little-endian builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/fsl-dpaa2-qdma/dpdmai.c -->
