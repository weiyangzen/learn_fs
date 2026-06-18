# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_hw_qp_ctxt.h

## Purpose
Defines the firmware-visible queue-pair context records for the original Huawei HiNIC driver. The file is a hardware contract header: it describes how SQ and RQ context blocks are packed before being sent through the command-queue path to initialize, clean, or reconfigure queue resources.

## Important APIs, Types, And Constants
The main exported types are `struct hinic_qp_ctxt_header`, `struct hinic_sq_ctxt`, `struct hinic_rq_ctxt`, `struct hinic_clean_queue_ctxt`, `struct hinic_sq_ctxt_block`, and `struct hinic_rq_ctxt_block`. `enum hinic_qp_ctxt_type` selects SQ or RQ contexts. Bitfield helpers such as `HINIC_SQ_CTXT_CEQ_ATTR_SET`, `HINIC_RQ_CTXT_PI_SET`, and `HINIC_*_WQ_BLOCK_SET` encode queue IDs, completion-event enable bits, producer/consumer indexes, page PFNs, and WQ block PFNs. `HINIC_SQ_CTXT_SIZE`, `HINIC_RQ_CTXT_SIZE`, and `HINIC_Q_CTXT_MAX` bound how many queue contexts fit in a `HINIC_CMDQ_BUF_SIZE` command buffer.

## Control Flow And State
This header has no executable flow; callers populate the structures and send them to firmware. The state represented is persistent device queue context: queue type, queue count, queue address offset, CI/PI positions, wrap bits, completion-event settings, WQ page addresses, prefetch cache hints, and physical WQ block addresses. PFNs are derived from DMA addresses with `HINIC_WQ_PAGE_PFN()` and `HINIC_WQ_BLOCK_PFN()`.

## Dependencies And Integration Points
It depends on `linux/types.h` and `hinic_hw_cmdq.h` for command-buffer sizing. It is coupled to queue allocation in `hinic_hw_wq.c` and queue-pair programming in `hinic_hw_qp.c`; those layers must supply DMA addresses and indices in the layout expected here. The big-endian/little-endian conversion policy is enforced by callers that marshal these records for firmware.

## Risks And Test Signals
The central risk is silent firmware misconfiguration from a wrong shift, mask, PFN granularity, or structure size. Tests/signals should include queue bring-up on SQ/RQ counts near `HINIC_Q_CTXT_MAX`, traffic after interface reopen, reset or queue-clean flows, and hardware error logs for invalid command buffers. Sparse or build checks help catch type regressions, but only device or emulator testing validates the packed ABI.
