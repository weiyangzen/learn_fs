# sources/distributed-fs/ceph-client/drivers/usb/host/xhci.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/usb/host/xhci.h` is the central private header for the Linux xHCI host-controller driver. It defines the controller MMIO register layouts, context structures, TRB/event encodings, ring and stream data structures, endpoint/device/roothub/interrupter/controller state containers, quirk flags, decode/debug helpers, inline conversion helpers, and cross-file prototypes used by `xhci.c`, ring code, memory code, hub code, trace/debugfs code, and bus-specific glue. The source was read as a complete 2613-line file for this report.

## Important APIs, Types, and Functions

Core hardware-facing types include `struct xhci_cap_regs`, `struct xhci_port_regs`, `struct xhci_op_regs`, `struct xhci_intr_reg`, `struct xhci_run_regs`, `struct xhci_doorbell_array`, `struct xhci_slot_ctx`, `struct xhci_ep_ctx`, `struct xhci_input_control_ctx`, `struct xhci_stream_ctx`, `union xhci_trb`, `struct xhci_erst_entry`, and `struct xhci_device_context_array`.

Software state types include `struct xhci_container_ctx`, `struct xhci_command`, `struct xhci_stream_info`, `struct xhci_bw_info`, `struct xhci_virt_ep`, `struct xhci_interval_bw_table`, `struct xhci_virt_device`, `struct xhci_root_port_bw_info`, `struct xhci_tt_bw_info`, `struct xhci_segment`, `struct xhci_td`, `struct xhci_ring`, `struct xhci_scratchpad`, `struct urb_priv`, `struct s3_save`, `struct xhci_bus_state`, `struct xhci_interrupter`, `struct xhci_port_cap`, `struct xhci_port`, `struct xhci_hub`, `struct xhci_hcd`, and `struct xhci_driver_overrides`.

Important macros encode xHCI register bits (`CMD_RUN`, `CMD_RESET`, `STS_HALT`, `STS_CNR`, `IMAN_IE`, `ERST_EHB`), context fields (`SLOT_FLAG`, `EP0_FLAG`, `LAST_CTX`, `ROOT_HUB_PORT`, `EP_TYPE`, `MAX_PACKET`, `TR_DEQ_PTR_MASK`), TRB fields and types (`TRB_NORMAL`, `TRB_SETUP`, `TRB_CONFIG_EP`, `TRB_TRANSFER`, `TRB_TYPE`, `TRB_CYCLE`, `TRB_CHAIN`, `TRB_IDT`, `TRB_TD_SIZE`), ring sizing (`TRBS_PER_SEGMENT`, `TRB_SEGMENT_SIZE`, `TRB_MAX_BUFF_SIZE`), completion codes (`COMP_SUCCESS`, `COMP_STALL_ERROR`, `COMP_COMMAND_ABORTED`, etc.), bandwidth constants, endpoint state bits, controller state bits, and a large quirk bitmap.

Inline helpers include HCD/controller conversion (`hcd_to_xhci`, `xhci_to_hcd`, `xhci_get_usb3_hcd`, `xhci_hcd_is_usb3`, `xhci_has_one_roothub`), 64-bit MMIO access (`xhci_read_64`, `xhci_write_64`), link TRB quirk selection, URB-to-transfer-ring lookup, IDT eligibility, and many trace/debug decoders for TRBs, control contexts, slot contexts, port status, USB status, doorbells, endpoint states, endpoint types, and endpoint contexts.

## Control Flow

This header does not own an independent runtime flow, but it defines the contracts that make the flow in `xhci.c` and companion files possible. The register structures map MMIO regions discovered during setup. Context structures are allocated by memory helpers, filled by setup/configuration helpers, and handed to hardware through command TRBs. Ring/TRB structures are manipulated by queueing and event handlers. State bits in `xhci_hcd`, `xhci_virt_ep`, and `xhci_virt_device` gate whether higher-level flows may touch hardware, queue URBs, clear toggles, allocate streams, or recover from port errors.

The prototype section connects the implementation units: memory/context helpers, ring queue helpers, command timeout handling, event interrupter management, roothub operations, power management, and generic HCD lifecycle methods. `xhci_driver_overrides` allows bus glue to replace selected methods while preserving the generic method table.

## State and Persistence Behavior

The header defines in-memory and hardware-visible state layouts. Hardware ABI state is persistent only while controller memory and MMIO programming remain valid: device contexts, endpoint contexts, stream contexts, TRBs, ERST entries, scratchpads, and register values must match xHCI layout and alignment requirements. Software state persists for the lifetime of the controller instance in `struct xhci_hcd`, for the lifetime of a USB device slot in `struct xhci_virt_device`, for endpoint configuration lifetimes in `struct xhci_virt_ep`, and for individual URBs in `struct urb_priv` and `struct xhci_td`.

No file-backed storage is defined. Suspend/resume state is represented in `struct s3_save` and interrupter `s3_*` fields. Debug decode helpers format state into caller-provided buffers and do not retain it.

## Dependencies and Integration Points

The header includes Linux USB/HCD, timer, kernel, bit, and 64-bit MMIO helpers plus xHCI-local capability, extended-capability, port, and PCI quirk headers. Its declarations integrate with `xhci-mem.c` for allocation and context manipulation, `xhci-ring.c` for TRB queueing/event processing, `xhci-hub.c` for roothub control and port state, `xhci.c` for generic HCD operations, debugfs/trace code for observability, bus glue for PCI/platform overrides, and USB core types such as `struct usb_hcd`, `struct usb_device`, `struct urb`, and endpoint descriptors.

## Risks and Edge Cases

The largest risk is ABI drift: hardware register/context/TRB structures must keep exact sizes, offsets, bit definitions, endian annotations, alignment, and write semantics. Incorrect bit masks can corrupt controller state, lose interrupts, misprogram endpoint rings, or misdecode completion events. State-bit combinations in endpoints and controller state are concurrency-sensitive because interrupt handlers, command completion, PM, and USB core callbacks share them. The quirk bitmap is broad and controller-specific; reusing, reordering, or misinterpreting bits can silently change behavior on unrelated hardware.

Debug decode helpers use fixed caller-provided buffers and `sprintf`/`snprintf`; callers must provide adequate buffer sizes. Several macros assume valid endpoint indices, slot IDs, intervals, and context flags. IDT eligibility intentionally excludes isochronous transfers despite possible spec support.

## Test Signals

Useful signals are allmodconfig/USB xHCI compile coverage, sparse/endian checking of `__le32`/`__le64` fields, module init layout assertions in `xhci.c`, trace/debug formatting smoke tests, ring and command tests that verify TRB field construction against expected bit encodings, endpoint index/address round-trip tests, suspend/resume register save/restore tests, and hardware enumeration/transfer coverage across controllers with different quirk combinations.
