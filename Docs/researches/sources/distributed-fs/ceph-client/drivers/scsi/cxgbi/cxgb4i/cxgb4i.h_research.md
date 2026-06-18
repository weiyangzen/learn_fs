# sources/distributed-fs/ceph-client/drivers/scsi/cxgbi/cxgb4i/cxgb4i.h

## Purpose

`cxgb4i.h` is the small adapter-specific public header for the Chelsio T4/T5/T6 iSCSI driver. It centralizes driver limits and transmit-header sizing used by `cxgb4i.c`, keeping the adapter module's constants separate from the common `libcxgbi` library.

## Important APIs, Types, And Functions

The header defines constants rather than functions or structs. `CXGB4I_SCSI_HOST_QDEPTH` sets the SCSI host queue depth to 1024. `CXGB4I_MAX_CONN` caps connections at 16384, and `CXGB4I_MAX_TARGET` mirrors that limit. `CXGB4I_MAX_LUN` sets the maximum LUN count to `0x1000`. `CXGB4I_TX_HEADER_LEN` computes the reserved skb transmit headroom required for a firmware offload TX_DATA work request plus the SGE opaque header. `T5_ISS_VALID` is a T5/T6 active-open option bit used when sending an initial send sequence value.

## Control Flow

The header has no runtime control flow. Its values feed `cxgb4i.c`: the host template uses queue and LUN limits; ULD/device initialization clamps the maximum connection count and sizes per-host resources; transmit PDU allocation uses the header length through `cdev->skb_tx_rsvd`; and T5/T6 active-open request construction sets `T5_ISS_VALID`.

## State And Persistence Behavior

There is no mutable state. The constants influence in-memory kernel object sizes, queue limits, and skb layout while the module is loaded. No value is persisted outside the loaded driver and adapter state created by the implementation file.

## Dependencies And Integration Points

`CXGB4I_TX_HEADER_LEN` depends on Chelsio firmware and SGE structures (`struct fw_ofld_tx_data_wr` and `struct sge_opaque_hdr`) being visible to the translation unit that includes the header. The limit constants integrate with Linux SCSI host sizing, libiscsi session sizing, and Chelsio TID/resource sizing in `cxgb4i.c`.

## Risks

The primary risk is size drift: if firmware WR or SGE header structures change and `CXGB4I_TX_HEADER_LEN` is not sufficient, transmit skbs can lack headroom when `cxgbi_sock_tx_queue_up()` prepares offload WRs. Connection and queue constants must also remain compatible with adapter TID limits; `cxgb4i.c` mitigates this by clamping against hardware TID counts, but oversized defaults still affect memory allocation and advertised host capacity.

## Test Signals

Compile coverage is the main signal for this header. Runtime signals include successful skb allocation and TX header push without headroom errors, host queue depth visible through SCSI/iSCSI host attributes, and connection-count clamping behavior during adapter registration.
