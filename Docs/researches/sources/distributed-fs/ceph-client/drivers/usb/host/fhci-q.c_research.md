# sources/distributed-fs/ceph-client/drivers/usb/host/fhci-q.c

## Purpose
`fhci-q.c` implements FHCI software queue manipulation and URB completion accounting. It maps FHCI TD hardware/status bits to Linux errno values, moves TDs among ED queues, frame queues, and the done list, updates URB lengths/statuses, and returns completed URBs to the USB core.

## Important APIs, Types, and Functions
- Queue operations: `fhci_add_tds_to_ed()`, `fhci_remove_td_from_ed()`, `fhci_add_td_to_frame()`, `fhci_remove_td_from_frame()`, `fhci_peek_td_from_frame()`, `fhci_remove_td_from_done_list()`, and `fhci_move_td_from_ed_to_done_list()`.
- Completion operations: `fhci_done_td()`, `fhci_urb_complete_free()`, and `fhci_del_ed_list()`.
- `status_to_error()` converts FHCI TD status bits into USB core status codes.

## Control Flow
URB queueing appends all TDs to an ED and sets `td_head` if idle. Scheduling moves a TD into the actual frame and, when hardware completion is confirmed, `fhci_move_td_from_ed_to_done_list()` removes the current head, advances the ED, updates toggle carry, appends the TD to `done_list`, and schedules the completion tasklet if IOC is set. The tasklet calls `fhci_done_td()` for each done TD, increments the URB completed-TD count, and either gives the URB back or handles delete/halt cleanup. Dequeue paths mark URBs for deletion and `fhci_del_ed_list()` removes TDs from EDs when safe.

## State and Persistence Behavior
Mutable state lives in linked lists (`ed->td_list`, `frame->tds_list`, `hc_list->done_list`), ED fields (`td_head`, `state`, `toggle_carry`), URB private counters, and URB aggregate status/actual length. `fhci_urb_complete_free()` recycles TDs, possibly removes idle EDs from schedules, decrements `active_urbs`, unlinks the URB from the USB core endpoint, drops the FHCI lock for `usb_hcd_giveback_urb()`, and reacquires it.

## Dependencies and Integration Points
The file integrates with FHCI scheduler completion, memory recycling, USB HCD endpoint linking/unlinking, and Linux URB semantics such as `URB_SHORT_NOT_OK`, iso frame descriptors, and endpoint toggles. It assumes lock ownership around list mutations and uses completion status values defined in `fhci.h`.

## Risks and Test Signals
Risks include list corruption if TDs are removed twice, lock reentry hazards around giveback, missing handling for null/stale `urb_priv` during asynchronous dequeue, and subtle short-packet semantics for control/bulk/iso. Test signals include short reads with and without `URB_SHORT_NOT_OK`, stall/NAK/timeout/error mapping, iso descriptor status updates, interrupt URB unlink, endpoint disable during active TDs, and active URB count returning to zero after stress cycles.
