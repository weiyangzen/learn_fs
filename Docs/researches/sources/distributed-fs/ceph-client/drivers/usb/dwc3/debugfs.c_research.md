# sources/distributed-fs/ceph-client/drivers/usb/dwc3/debugfs.c

## Purpose
`debugfs.c` exposes DWC3 diagnostic and control surfaces under the USB debugfs root. It provides a broad register dump, LSP mux access, current mode reporting and role switching, gadget test-mode control, link-state display/control, and per-endpoint FIFO/queue/TRB/debug-register views.

## Important APIs, Types, and Functions
The file defines `dwc3_regs[]`, a `debugfs_reg32` table spanning global, PHY, FIFO, event, device, endpoint, and OTG registers. Public functions are `dwc3_debugfs_init()`, `dwc3_debugfs_exit()`, `dwc3_debugfs_create_endpoint_dir()`, and `dwc3_debugfs_remove_endpoint_dir()`. File operations cover `lsp_dump`, `mode`, `testmode`, `link_state`, and endpoint attributes such as `tx_fifo_size`, `rx_fifo_size`, request queues, `transfer_type`, `trb_ring`, and `GDBGEPINFO`.

## Control Flow
Initialization allocates `dwc->regset`, initializes `dbg_lsp_select`, creates a per-device directory, installs `regdump`, `lsp_dump`, optional dual-role `mode`, and optional gadget `testmode`/`link_state` files. Endpoint directories are created later by gadget endpoint setup and contain the endpoint map files. Most read paths call `pm_runtime_resume_and_get()`, take `dwc->lock`, read relevant DWC3 registers, format with `seq_file`, unlock, and drop runtime PM. Write paths parse small user buffers, then update `dbg_lsp_select`, call `dwc3_set_mode()`, call `dwc3_gadget_set_test_mode()`, or request a gadget link-state transition.

## State and Persistence Behavior
The only additional controller state is `dwc->regset`, `dwc->debug_root`, and `dwc->dbg_lsp_select`. Debugfs writes change live hardware/controller state but are not persistent across unload, reset, or reboot. Endpoint debug views read live rings and FIFO state; they do not snapshot or store history.

## Dependencies and Integration Points
The file integrates debugfs, seq_file, runtime PM, the DWC3 register accessors, `core.h` register definitions, `debug.h` string helpers, and gadget helpers for test mode/link-state control. It is initialized from `dwc3_core_probe()` after the core is initialized and removed before core exit.

## Risks
Debugfs is privileged but still dangerous: role switching, test mode, and link-state writes can disrupt active traffic. Register dump coverage includes fixed slots for ports/FIFOs/endpoints and must remain aligned with multiport limits. Runtime PM failure handling is basic, and live TRB-ring reads depend on the endpoint lock preventing concurrent mutation. The endpoint debug directory remove path uses lookup-and-remove by name, so endpoint naming consistency matters.

## Test Signals
Mount debugfs and verify `regdump`, `lsp_dump`, `mode`, `testmode`, and `link_state` appear according to Kconfig/mode. Exercise reads during runtime suspend and active transfer. In gadget mode, check link-state and test-mode writes. In dual-role mode, write `host`, `device`, and `otg` to `mode`. For endpoints, confirm FIFO and TRB files are created/removed with endpoint enable/disable and do not crash on EP0.
