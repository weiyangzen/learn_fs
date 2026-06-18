<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/cdns2/cdns2-ep0.c -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/cdns2/cdns2-ep0.c

## Purpose
This file implements endpoint zero for the Cadence USBHS gadget driver: setup packet handling, standard control requests, EP0 DMA/TRB submission, status stages, stalls, delayed status completion, and EP0 endpoint operations.

## Important APIs, Types, And Functions
The EP0 descriptor is `cdns2_gadget_ep0_desc`. Helpers include `cdns2_w_index_to_ep_index()`, `cdns2_check_new_setup()`, `cdns2_ep0_enqueue()`, `cdns2_ep0_delegate_req()`, `cdns2_ep0_stall()`, and `cdns2_status_stage()`. Standard request handlers include `cdns2_req_ep0_set_configuration()`, `cdns2_req_ep0_set_address()`, `cdns2_req_ep0_handle_status()`, and feature helpers for device/interface/endpoint recipients. Public internal entry points are `cdns2_handle_setup_packet()`, `cdns2_handle_ep0_interrupt()`, `cdns2_pending_setup_status_handler()`, `cdns2_ep0_config()`, and `cdns2_init_ep0()`. EP0 ops are queue/dequeue through `cdns2_gadget_ep0_ops`.

## Control Flow
On SUDAV, `cdns2_handle_setup_packet()` acknowledges setup-change state, reads eight setup bytes, drops stale reads if the setup buffer changed mid-read, clears EP0 stall state, cancels any pending EP0 request, chooses data or status stage, sets transfer direction, reconciles auto-applied SET_ADDRESS from the function-address register, handles standard requests locally when possible, delegates other requests to the gadget driver, then either stalls or sends status. EP0 queued data requests are DMA-mapped, put on the pending list, optionally expanded with a ZLP TRB, and started by `cdns2_ep0_enqueue()`. EP0 DMA interrupts call `cdns2_transfer_completed()` and then status stage.

## State And Persistence
EP0 state is shared through `pdev->setup`, `pdev->ep0_stage`, `pdev->dev_address`, `pdev->may_wakeup`, `pdev->pending_status_request`, `status_completion_no_call`, `ep0_preq`, and `eps[0].pending_list`. The EP0 transfer ring uses the first two TRBs for data and optional ZLP.

## Dependencies And Integration Points
The file integrates with the generic CDNS2 gadget helpers (`cdns2_select_ep()`, request allocation/free, giveback, halt), USB composite/ch9 semantics, DMA mapping by device, tracepoints, and controller registers defined in `cdns2-gadget.h`.

## Risks
SET_ADDRESS is acknowledged automatically by hardware, so the driver must infer missed address changes from `fnaddr`. Status-stage completion has no interrupt and is completed asynchronously via `system_freezable_wq`, which is a race-sensitive integration point. Only one EP0 data request is allowed at a time; a new setup cancels pending work. The endpoint feature handler maps `wIndex` directly into `pdev->eps[]`, so invalid endpoint indexes rely on upstream request validity.

## Test Signals
Test enumeration, SET_ADDRESS, SET_CONFIGURATION with delayed status, GET_STATUS for device/interface/endpoint, remote wake enable/disable, endpoint halt/clear-halt with wedge, test mode requests, ZLP on EP0 IN, new setup overriding pending data, and EP0 stall recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/cdns2/cdns2-ep0.c -->
