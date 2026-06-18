<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/mod_host.c -->
# sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/mod_host.c

## Purpose
USB host controller frontend for Renesas USBHS. It wraps the controller as a `usb_hcd`, emulates a one-port root hub, maps devices/endpoints onto limited reusable hardware pipes, and translates URBs into `usbhs_pkt` transfers.

## Important APIs, Types, And Functions
`struct usbhsh_hpriv` embeds `usbhs_mod`, DCP pipe, fixed device slots, port status, and setup ACK completion. `struct usbhsh_device` maps `usb_device` to a DEVADD slot. `struct usbhsh_ep` maps host endpoint to pipe. `struct usbhsh_request` wraps URB and packet. The `hc_driver` implements URB enqueue/dequeue, endpoint disable, hub status/control, and no-op bus suspend/resume. IRQ callbacks handle attach, detach, setup ACK, and setup error.

## Control Flow
Probe creates an HCD and registers host mode. Start adds the HCD, initializes FIFO/pipe, creates host pipes with direction assignment, enables host mode, and installs IRQ callbacks. URB enqueue links the URB, attaches device and endpoint metadata if needed, attaches a compatible pipe, then queues DCP setup/data/status or a normal packet. Completion updates length, saves DATA toggle for reused pipes, detaches pipe, unlinks, and gives back the URB. Root-hub reset drives bus reset, waits for speed, and enables SOF.

## State And Persistence
HCD private state, device slots, endpoint lists/counters, port-status bits, setup completion, URB/endpoint private pointers, USB device drvdata, and USB core DATA toggles. Hardware state includes DEVADDn, DCP/PIPE, FIFO, and host-mode registers.

## Dependencies And Integration Points
Depends on USB HCD APIs, root-hub request definitions, and internal common/mod/pipe/FIFO layers.

## Risks
Limited device slots and pipes are central failure modes. Setup waits for SACK/SIGN completion and can hang if interrupts are lost. SET_ADDRESS rewrites the USB address to the internal slot number. Isochronous URBs are rejected. Error unwind after URB linking deserves close review in this source snapshot.

## Test Signals
Attach/detach, root-hub reset/speed detection, SET_ADDRESS, hub devices, slot exhaustion, endpoint disable with queued URBs, bulk/interrupt IN/OUT, DATA toggle correctness, URB dequeue, and missing setup ACK/error interrupts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/mod_host.c -->
