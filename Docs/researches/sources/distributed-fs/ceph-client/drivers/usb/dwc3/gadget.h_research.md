# sources/distributed-fs/ceph-client/drivers/usb/dwc3/gadget.h

Purpose: declares DWC3 gadget-side constants, endpoint/request conversion helpers, request-list helpers, and cross-file gadget APIs used by gadget, EP0, and core code.

Important APIs/types/functions: defines DEPCFG/DEPXFERCFG bit builders, U1/U2 latency defaults, `DWC3_FRNUMBER_MASK`, `to_dwc3_ep`, `to_dwc3_request`, `gadget_to_dwc`, `next_request`, `dwc3_gadget_move_started_request`, `dwc3_gadget_move_cancelled_request`, `dwc3_gadget_ep_get_transfer_index`, and `dwc3_gadget_dctl_write_safe`. It declares EP0 helpers, request giveback, halt setting, delayed status, active transfer stop, and start-config entry points.

Control flow: inline helpers are used in the request lifecycle. Queued requests are moved to `started_list` when TRBs are prepared and to `cancelled_list` when dequeue, stall clearing, disconnect, or transfer errors require later cleanup. `dwc3_gadget_ep_get_transfer_index` reads `DEPCMD` after `STARTTRANSFER`; `dwc3_gadget_dctl_write_safe` preserves link-state request bits during DCTL read-modify-write operations.

State and persistence: this header does not allocate state, but it defines how list membership and request status values are updated. Its bit macros encode persistent hardware register state in endpoint configuration commands and device control writes.

Dependencies and integration: includes Linux list and USB gadget headers plus `io.h`; depends on `core.h` types through included IO helpers. It is the local contract between `gadget.c`, `ep0.c`, and any DWC3 code that issues endpoint commands or manipulates gadget request lists.

Risks: these helpers assume callers hold the DWC3 lock. Misusing the move helpers can corrupt endpoint request lists. `dwc3_gadget_dctl_write_safe` is important because accidental nonzero `ULSTCHNGREQ` writes can request a link transition. The DEPCFG macros are low-level register encodings, so off-by-one endpoint numbers, FIFO numbers, burst sizes, or interval values lead to hardware misconfiguration.

Test signals: compile coverage is the main direct signal. Runtime validation appears through successful endpoint configuration, EP0 control traffic, stalled endpoint recovery, transfer-resource allocation, and absence of unexpected link-state changes during DCTL writes.
