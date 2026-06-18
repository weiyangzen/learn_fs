# sources/distributed-fs/ceph-client/drivers/usb/cdns3/cdns3-gadget.h

Purpose: Defines the CDNS3 device-controller register map, bit fields, TRB format, endpoint/request/device data structures, constants, and cross-file gadget function prototypes.

Important APIs, types, and functions: `struct cdns3_usb_regs` maps the device register block. Macros define global USB config/status/command/interrupt bits, endpoint select/config/command/status bits, TRB fields, capability parsing, DMA AXI settings, versions, ring sizes, endpoint limits, and workaround buffer sizes. `struct cdns3_trb` is the hardware transfer descriptor. `struct cdns3_endpoint` stores Linux endpoint object, request lists, TRB ring, endpoint flags, direction/type/interval, ring producer-consumer state, workaround state, stream state, and TDL tracking. `struct cdns3_request` wraps `usb_request` with TRB indexes and flags. `struct cdns3_device` is the gadget controller state. Prototypes expose the gadget/ep0 shared functions.

Control flow: The header does not run control flow, but its constants encode how implementation files select endpoints, program TRBs, determine speeds, configure endpoint buffering, handle interrupts, and track endpoint lifecycle.

State and persistence behavior: The defined structs describe in-memory state only. `cdns3_device` owns DMA pools, setup/ZLP buffers, endpoint array, selected endpoint cache, status work, and feature flags. `cdns3_endpoint` tracks pending/deferred/internal request lists and ring indexes. No persistent storage is involved.

Dependencies and integration points: Includes Linux gadget and DMA direction headers. Used by `cdns3-gadget.c`, `cdns3-ep0.c`, debug helpers, and trace definitions. It is tightly coupled to Cadence USBSS hardware ABI and Linux gadget core types.

Risks: Register bit macros are hardware-critical. Some macros appear parameterized but reference `p` in bodies for link-state helpers, so callers must use only valid macros and compile coverage matters. Ring-size constants affect memory use and isochronous behavior. Endpoint flags are a dense bitfield contract across multiple files; adding flags or changing semantics requires auditing queue, completion, halt, and reset paths.

Test signals: Compile all CDNS3 gadget configurations, run sparse/clang warnings over macro usage, validate register field programming on hardware or emulation, exercise all endpoint types and stream modes, and inspect trace/debug dumps for ring index/cycle consistency.
