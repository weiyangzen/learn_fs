# sources/distributed-fs/ceph-client/drivers/usb/host/fhci-mem.c

## Purpose
`fhci-mem.c` owns FHCI software ED/TD object initialization, free-list recycling, and TD population. It is the allocator-facing layer used by URB scheduling to avoid repeated dynamic allocation in normal interrupt-driven paths.

## Important APIs, Types, and Functions
- `fhci_recycle_empty_td()` and `fhci_recycle_empty_ed()` reset and return TD/ED objects to controller free lists.
- `fhci_get_empty_ed()` and internal `get_empty_td()` remove objects from free lists or allocate fallback objects with `GFP_ATOMIC`.
- `fhci_td_fill()` initializes a TD for a URB stage and stores it in `urb_priv->tds[index]`.
- Internal `init_td()` and `init_ed()` zero objects and initialize list heads.

## Control Flow
At controller start, `fhci_mem_init()` in `fhci-hcd.c` preallocates `MAX_TDS` and `MAX_EDS` and recycles them through these helpers. URB construction in `fhci_queue_urb()` calls `fhci_td_fill()` for setup/data/status, bulk fragments, interrupt TDs, or iso packet descriptors. Each TD captures the URB, ED, transaction type, data pointer, length, toggle, iso index, interval, start frame, IOC flag, and initial OK status. Completion paths recycle TDs and EDs through the reset helpers.

## State and Persistence Behavior
The persistent state is the controller's in-memory `empty_tds` and `empty_eds` lists. Recycling deliberately clears prior runtime fields such as packet pointers, counters, statuses, and list links, which prevents stale TD/ED state from contaminating later URBs. There is no external persistence.

## Dependencies and Integration Points
The file depends on `fhci.h` structures, kernel slab/list APIs, and FHCI queue/scheduler code. It assumes callers hold the appropriate FHCI lock when manipulating shared lists. Fallback `GFP_ATOMIC` allocation allows continued operation if the preallocated pool is exhausted, but logs allocation failures with `fhci_err()`.

## Risks and Test Signals
Risks include pool exhaustion under many active URBs, unchecked `fhci_td_fill()` failures in callers, and dependence on correct object recycling order. Test signals include stress enqueue/dequeue beyond `MAX_TDS`/`MAX_EDS`, allocation-failure injection, repeated endpoint disable/reuse cycles, and verifying that recycled TDs do not retain stale `frame_lh`, `pkt`, `error_cnt`, or `nak_cnt` state.
