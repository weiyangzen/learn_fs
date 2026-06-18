# sources/distributed-fs/ceph-client/drivers/usb/cdns3/cdnsp-gadget.c

Purpose: main CDNSP USB gadget controller implementation. The complete 2077-line file was read. It initializes registers and DMA state, registers the UDC, exposes endpoint/gadget ops, manages slot/device/endpoint commands, handles link/speed/power behavior, and plugs the gadget role into the shared Cadence DRD core.

Important APIs/types/functions: `cdnsp_port_speed()`, `cdnsp_port_state_to_neutral()`, `cdnsp_find_next_ext_cap()`, `cdnsp_set_link_state()`, `cdnsp_halt()`, `cdnsp_died()`, `cdnsp_reset()`, `cdnsp_ep_enqueue()`, `cdnsp_ep_dequeue()`, `cdnsp_wait_for_cmd_compl()`, `cdnsp_halt_endpoint()`, `cdnsp_reset_device()`, `cdnsp_alloc_streams()`, slot enable/disable, `cdnsp_setup_device()`, `cdnsp_set_usb2_hardware_lpm()`, `cdnsp_update_erst_dequeue()`, gadget suspend/resume/disconnect/reset helpers, and `cdnsp_gadget_init()`.

Control flow: role init allocates `cdnsp_device`, powers gadget mode, runs generic setup, initializes memory and endpoints, registers the UDC, and requests threaded IRQs. UDC start runs the controller at the bounded speed and enables interrupts. Endpoint ops configure contexts/rings, map and queue requests, dequeue/cancel, halt/wedge, and free rings on disable. Stop disables ports/slot/IRQs, consumes events, clears command ring state, and unbinds the gadget.

State and persistence: persistent runtime state is `struct cdnsp_device`: register windows, capabilities, lock, gadget driver, contexts, rings, endpoint array, ports, DMA pools, setup buffer, state flags, and link state. Endpoint objects persist enabled/stopped/halted/wedged/stream/unconfigured state.

Dependencies/integration: Linux gadget core, request DMA mapping, threaded IRQs, Cadence DRD role/VBUS helpers, DMA APIs, PM, tracepoints, and companion memory/ring/EP0 files. It also applies CDNSP hardware workarounds via extended capabilities.

Risks: command completion timeouts mark hardware dying; endpoint disable must stop, dequeue, invalidate events, and update contexts without racing disconnect; remote wakeup must respect host-enabled wake state; DMA mask, 64-bit register ordering, stream limits, and workaround bits are hardware-sensitive.

Test signals: UDC bind/unbind, full/high/super/super-plus enumeration, all endpoint types enable/disable, transfer loops, cancellation, halt/wedge/clear, disconnect/reconnect, suspend/resume/wakeup, pullup toggling, command-timeout/fatal paths, and trace agreement for commands and port changes.
