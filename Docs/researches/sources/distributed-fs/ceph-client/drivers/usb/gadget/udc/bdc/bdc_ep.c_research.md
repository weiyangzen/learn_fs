<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/bdc/bdc_ep.c -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/bdc/bdc_ep.c

## Purpose
This file implements BDC endpoint allocation, buffer descriptor list management, request queueing and completion, EP0 control-transfer handling, transfer status report processing, and USB endpoint operations.

## Important APIs, Types, And Functions
BD list helpers include `ep_bd_list_alloc()`, `ep_bd_list_free()`, `chain_table()`, `bd_needed_req()`, `bd_available_ep()`, `bdi_to_bd()`, `bd_add_to_bdi()`, and `ep_bdlist_eqp_adv()`. Transfer setup is handled by `setup_bd_list_xfr()`, `bdc_queue_xfr()`, `bdc_notify_xfr()`, and `bdc_req_complete()`. Endpoint lifecycle uses `bdc_ep_enable()`, `bdc_ep_disable()`, `bdc_free_ep()`, and `bdc_init_ep()`. EP0 control logic includes `ep0_queue_status_stage()`, `ep0_queue_data_stage()`, `handle_control_request()`, `ep0_handle_status()`, `ep0_handle_feature()`, `bdc_xsf_ep0_setup_recv()`, `bdc_xsf_ep0_data_start()`, `bdc_xsf_ep0_status_start()`, and `ep0_xsf_complete()`. Gadget endpoint ops are implemented by `bdc_gadget_ep_enable()`, `bdc_gadget_ep_disable()`, `bdc_gadget_ep_queue()`, `bdc_gadget_ep_dequeue()`, `bdc_gadget_ep_set_halt()`, and request alloc/free helpers.

## Control Flow
Endpoint enable allocates chained BD tables, configures the hardware endpoint, and marks it enabled. Queuing maps the request, verifies transfer length, calculates needed BDs, writes one or more descriptors, clears stop-buffer-fetch on the first descriptor after a memory barrier, appends the request to the queue, and notifies the controller. Status reports enter `bdc_sr_xsf()`, dispatch by XSF status, complete normal or short transfers through `handle_xsr_succ_status()`, or drive EP0 setup/data/status state transitions. Dequeue stops the endpoint, compares request BD range with the hardware dequeue pointer, and either converts the request start to a chain descriptor or issues a BLA command to skip to the next transfer.

## State And Persistence
Each endpoint owns a BD ring-like list of tables, enqueue/dequeue indexes, endpoint flags (`BDC_EP_ENABLED`, `BDC_EP_STALL`, `BDC_EP_STOP`), an outstanding request list, and an `ignore_next_sr` flag for multi-BD short transfers. EP0 state persists in `bdc->ep0_state`, `setup_pkt`, delayed status flag, ZLP flag, standard-request response buffer, test mode, and device status bits.

## Dependencies And Integration Points
The file depends on command helpers, USB gadget mapping/giveback APIs, USB composite/ch9 request semantics, status reports from `bdc_udc.c`, and register/descriptor definitions in `bdc.h`.

## Risks
BD ring accounting is subtle because chain descriptors are excluded from availability and wrap behavior. Short multi-BD transfers require ignoring an extra status report. EP0 delayed status and ZLP handling interact with control request direction and host `wLength`; mistakes can stall enumeration. `bdc_gadget_ep_queue()` requires non-NULL complete callbacks and buffers, so zero-length non-EP0 requests still need a valid buffer. Dequeue behavior depends on accurate hardware dequeue reads and correct chain descriptor rewriting.

## Test Signals
Run enumeration, GET_STATUS/SET_FEATURE/CLEAR_FEATURE, SET_SEL, test mode, delayed-status gadget functions, zero-length packet cases, short transfers with `short_not_ok`, multi-BD requests above 64 KiB, dequeue of head and non-head requests, endpoint stall/wedge, and isochronous endpoint enable if hardware exposes it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/bdc/bdc_ep.c -->
