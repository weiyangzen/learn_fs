# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/fsl_usb2_udc.h

## Purpose

`fsl_usb2_udc.h` is the private hardware and driver-state header for the Freescale USB DR gadget driver. It defines the device/host/system-interface register layouts, controller bit fields, endpoint queue-head and transfer-descriptor formats, alignment constraints, endpoint/request/controller private structures, ep0 state constants, and pipe/endpoint helper macros used by `fsl_udc_core.c`.

## Important APIs, Types, and Functions

The register map types are `struct usb_dr_device`, `struct usb_dr_host`, and `struct usb_sys_interface`. The DMA data structures are `struct ep_queue_head` for dQH entries and `struct ep_td_struct` for dTD entries. Driver-private types are `struct fsl_req`, `struct fsl_ep`, and `struct fsl_udc`. Helper macros include `ep_index()`, `ep_maxpacket()`, `ep_is_in()`, `get_ep_by_pipe()`, `get_pipe_by_windex()`, `get_pipe_by_ep()`, and the inline `get_qh_by_ep()`.

The constants cover USB command/status/interrupt bits, device address and endpoint-list registers, port status/control bits, OTG status/control bits, USB mode bits, endpoint control bits, snoop/system-interface control bits, dQH and dTD bit fields, DMA alignment requirements, endpoint directions, and ep0 transfer states.

## Control Flow

This header has no independent runtime control flow, but it defines the hardware contract that drives the implementation. Probe and controller setup use `usb_dr_device` and `usb_sys_interface` to map register offsets. Endpoint configuration uses endpoint-control bit fields plus `ep_queue_head` capability fields. Request queueing builds `ep_td_struct` chains using the dTD masks, alignment, packet-size, IOC, active, halt, and error bits. Completion walks the same descriptors and maps pipes back to `struct fsl_ep` instances through the helper macros. Ep0 direction is special: `get_qh_by_ep()` chooses between the two ep0 queue heads based on `udc->ep0_dir` because the driver exposes one ep0 object but hardware has separate IN and OUT dQHs.

## State and Persistence Behavior

The header describes volatile kernel and hardware state only. `struct fsl_udc` persists for the lifetime of the platform device and contains the active gadget binding, endpoint array, coherent queue-head allocation, status request, dTD pool, current USB state, ep0 state, endpoint direction, bus reset state, and VBUS/softconnect/OTG flags. `struct fsl_ep` persists per logical endpoint and owns the software queue. `struct fsl_req` persists per submitted request and owns its dTD chain until completion. No durable storage is involved.

## Dependencies and Integration Points

The header depends on `linux/usb/ch9.h` and `linux/usb/gadget.h` for standard USB request, endpoint, gadget, and descriptor definitions. It also depends on Freescale platform enums such as `enum fsl_usb2_phy_modes` supplied through included platform data in the C file. It is tightly coupled to the controller's dQH/dTD DMA format, the gadget framework's endpoint/request model, and platform-data fields for PHY mode, system-interface registers, endian mode, and controller version.

## Risks and Test Signals

Important risks are register-layout drift, wrong bit definitions, endian assumptions for dQH/dTD fields, alignment or DMA-boundary mismatches, and helper macros that depend on ep0 direction or endpoint descriptors being initialized. The `max_pipes` member is used by reset code and must be initialized coherently with `max_ep`; stale or zero values would skip queue reset. Test signals include compile coverage of all macro users, probe on controllers with different endpoint counts and PHY modes, ep0 IN and OUT transfers that exercise `get_qh_by_ep()`, multi-dTD transfers that cross 4 KiB pages, big-endian descriptor platforms, and reset paths that iterate all pipes.
