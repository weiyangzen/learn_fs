<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfa_port.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfa_port.c

## Purpose
`bfa_port.c` implements the physical port service module and the CEE service module for the BFA driver. The physical port half handles firmware mailbox requests for port enable, port disable, port statistics retrieval, statistics clearing, IOC event cleanup, DMA-backed stats buffers, and D-port/PBC gating. The CEE half handles firmware mailbox requests for CEE attributes, CEE statistics, and CEE statistics reset.

## Important APIs, Types, And Functions
Physical port public APIs are `bfa_port_meminfo()`, `bfa_port_mem_claim()`, `bfa_port_enable()`, `bfa_port_disable()`, `bfa_port_get_stats()`, `bfa_port_clear_stats()`, `bfa_port_notify()`, `bfa_port_attach()`, and `bfa_port_set_dportenabled()`. Internal helpers include `bfa_port_stats_swap()`, enable/disable/stat ISR completion helpers, and `bfa_port_isr()`.

CEE public APIs are `bfa_cee_meminfo()`, `bfa_cee_mem_claim()`, `bfa_cee_get_attr()`, `bfa_cee_get_stats()`, `bfa_cee_reset_stats()`, and `bfa_cee_attach()`. Internal CEE helpers include `bfa_cee_get_attr_isr()`, `bfa_cee_get_stats_isr()`, `bfa_cee_reset_stats_isr()`, `bfa_cee_isr()`, and `bfa_cee_notify()`.

The file uses BFI mailbox payloads such as `struct bfi_port_generic_req_s`, `struct bfi_port_get_stats_req_s`, `union bfi_port_i2h_msg_u`, `struct bfi_cee_get_req_s`, `struct bfi_cee_reset_stats_s`, `struct bfi_cee_get_rsp_s`, and `union bfi_cee_i2h_msg_u`. It exchanges data through DMA objects embedded in `struct bfa_port_s` and `struct bfa_cee_s`.

## Control Flow
Port attach initializes `struct bfa_port_s`, registers `bfa_port_isr()` for `BFI_MC_PORT`, adds an IOC notification callback, and initializes the stats reset timestamp. Memory setup computes one aligned stats buffer with `bfa_port_meminfo()` and stores its KVA/physical address in `bfa_port_mem_claim()`.

Port enable and disable first reject operations if PBC disabled, IOC disabled, IOC non-operational, D-port enabled, or another enable/disable is pending. On success they fill `port->endis_mb`, store callback context, set `endis_pending`, build a `BFI_PORT_H2I_ENABLE_REQ` or `BFI_PORT_H2I_DISABLE_REQ` header with the IOC port ID, and queue the mailbox through `bfa_ioc_mbox_queue()`. Firmware responses enter `bfa_port_isr()`, which ignores stale responses if the pending flag is already clear, then clears the flag and invokes the stored callback.

Stats retrieval checks IOC operational state and `stats_busy`, stores the caller's stats buffer and callback context, writes the DMA address into the request, and queues `BFI_PORT_H2I_GET_STATS_REQ`. Completion copies from the module's DMA buffer into the caller's buffer, swaps 32-bit pairs to host order with `bfa_port_stats_swap()`, computes `secs_reset` from `ktime_get_seconds()` and `stats_reset_time`, clears busy, and calls back. Stats clear queues `BFI_PORT_H2I_CLEAR_STATS_REQ`; completion refreshes `stats_reset_time`, clears busy, and calls back.

IOC disable/failure notification fails any outstanding port stats or enable/disable operation with `BFA_STATUS_FAILED`, clears callbacks and pending flags, and clears D-port state. CEE attach similarly registers `bfa_cee_isr()` for `BFI_MC_CEE` and adds an IOC notification callback. CEE get-attr/get-stats/reset-stats each enforce IOC operational state and one outstanding operation of the same type, fill the appropriate mailbox command, set callback context, and queue it. CEE ISR dispatches firmware responses by message ID, copies DMA payloads on success, performs limited endian conversion, clears pending state, and invokes callbacks.

## State And Persistence
The port module maintains pending-operation state in `stats_busy`, `endis_pending`, callback fields, status fields, `stats_reset_time`, `pbc_disabled`, and `dport_enabled`. DMA-backed stats are transient: firmware writes into `port->stats_dma.kva`, and completion copies into the caller-supplied `union bfa_port_stats_u`. `secs_reset` is derived from kernel time and is not firmware-persistent.

CEE state tracks independent pending flags and statuses for get-attr, get-stats, and reset-stats, plus callback contexts and DMA buffers for attributes/statistics. The implementation has no on-disk persistence; firmware/adapter state is reached through BFI mailbox commands.

## Dependencies And Integration Points
The file includes `bfad_drv.h`, `bfa_defs_svc.h`, `bfa_port.h`, `bfi.h`, and `bfa_ioc.h`. It integrates tightly with IOC mailbox dispatch (`bfa_ioc_mbox_regisr()`, `bfa_ioc_mbox_queue()`), IOC health checks (`bfa_ioc_is_disabled()`, `bfa_ioc_is_operational()`), IOC notification queues, DMA address formatting (`bfa_dma_be_addr_set()`), and BFI message classes `BFI_MC_PORT` and `BFI_MC_CEE`.

## Risks And Test Signals
Risks include stale firmware responses after local timeout/failure, callbacks invoked while upper layers are tearing down, incorrect endianness conversion for port and CEE stats, single-pending-operation busy semantics surprising callers, null callback handling for enable/disable paths, and inconsistent cleanup if IOC failure races with mailbox ISR completion. `bfa_cee_get_attr()` and `bfa_cee_get_stats()` overwrite `cee->attr` and `cee->stats` with caller buffers after `bfa_cee_mem_claim()` initially points them at DMA memory; the ISR copies from DMA KVA into those caller buffers, so callers must keep buffers valid until callback.

Good test signals include enable/disable success and failure callbacks, PBC-disabled and D-port-enabled rejection, IOC disabled/non-operational rejection, duplicate request `BFA_STATUS_DEVBUSY`, stale response ignored after failure cleanup, stats DMA copy and endian conversion validation, `secs_reset` behavior after clear, IOC failure completing all pending port and CEE operations with `BFA_STATUS_FAILED`, and CEE LLDP field endian conversion for `time_to_live` and `enabled_system_cap`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfa_port.c -->
