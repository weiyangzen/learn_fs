# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/aspeed-vhub/vhub.h

## Purpose
Defines the Aspeed vHub driver's hardware register map, bit fields, shared data structures, debug macros, DMA ordering workaround, and cross-file function prototypes. It is the shared contract among the vHub core, hub emulation, downstream device handling, EP0 handling, and generic endpoint handling.

## Important APIs, Types, And Functions
The header defines root vHub registers (`AST_VHUB_CTRL`, `AST_VHUB_CONF`, interrupt registers, EP0/EP1 registers, setup buffers), per-device registers (`AST_VHUB_DEV_*`), per-endpoint registers (`AST_VHUB_EP_*`), software reset bits, interrupt masks, EP config fields, DMA status fields, and descriptor word fields. Constants encode the legacy defaults of 15 generic endpoints, 5 ports, 64-byte EP0, 1024-byte EPn, and 256 descriptors.

Core types are `struct ast_vhub_desc`, `struct ast_vhub_req`, `enum ep0_state`, `struct ast_vhub_ep`, `struct ast_vhub_dev`, `struct ast_vhub_port`, `struct ast_vhub_full_cdesc`, and `struct ast_vhub`. The `to_ast_req`, `to_ast_ep`, and `to_ast_dev` helpers bridge Linux gadget objects back to driver-private objects. `enum std_req_rc` standardizes internal control-request handler results: stall, complete, data, or pass-to-driver.

The inline `vhub_dma_workaround` is a hardware-specific memory ordering primitive. It issues a barrier and dummy raw read from memory before MMIO writes that cause USB DMA, avoiding stale descriptor/buffer reads on Aspeed bus arbitration.

## Control Flow
The header does not run control flow by itself, but it defines the call graph between compilation units. `core.c` supplies request completion, nuking, request allocation, and hardware init. `ep0.c` supplies setup/ACK handling and control replies. `hub.c` supplies vHub hub request handling and bus/port state changes. `dev.c` supplies virtual downstream gadget lifecycle and standard device requests. `epn.c` supplies non-control endpoint ACK handling, stall updates, and endpoint allocation. Shared structures allow all these files to operate under a single `struct ast_vhub` lock and hardware register mapping.

## State And Persistence Behavior
The state model is entirely runtime. `struct ast_vhub` owns the platform device, MMIO base, IRQ, lock, clock/reset, EP0 coherent buffers, hub EP0, port array, endpoint pool, bus state, and descriptor copies. `struct ast_vhub_dev` represents a downstream virtual gadget with gadget-core state, driver pointer, port device, EP0, and endpoint pointer table. `struct ast_vhub_ep` represents either EP0 or generic EPn via a union, with request queues and DMA resources. Nothing here persists across driver unbind or reboot except hardware state initialized elsewhere.

## Dependencies And Integration Points
Includes USB core and hub chapter definitions (`linux/usb.h`, `linux/usb/ch11.h`) and assumes Linux gadget types are visible through implementation files. The register definitions map directly to Aspeed vHub hardware and are consumed by all vHub source files. Debug macros integrate with `CONFIG_USB_GADGET_VERBOSE` and `CONFIG_USB_GADGET_DEBUG`.

## Risks
This header is a high-blast-radius contract: changing bit definitions, structure layout expectations, or helper semantics affects every vHub component. The comment that EP0 device control bits must match vHub EP0 control bits is important for shared EP0 code. `VHUB_EP_TOGGLE_SET_EPNUM` and endpoint numbering must match hardware global endpoint indices, not just USB endpoint addresses. The DMA workaround is easy to mistake for an unnecessary read but documents a confirmed hardware race; bypassing it can break otherwise correct transfer code. Legacy constants are kept for AST2400/AST2500 compatibility, while newer revisions may use device tree sizing, so code should prefer runtime `max_ports` and `max_epns` where available.

## Test Signals
Header changes should be validated by building all Aspeed vHub objects, probing on supported SoCs, enumerating the hub with multiple downstream gadgets, exercising EP0 control requests and EPn DMA, and checking suspend/resume/reset. Compile-time failures in any vHub file, descriptor size build assertions, missing debug macro fields, or DMA data corruption after register/structure edits are strong signals.
