# sources/distributed-fs/ceph-client/drivers/net/wan/fsl_ucc_hdlc.c

Purpose: Freescale QUICC Engine UCC Fast HDLC driver. It programs UCC Fast, optional TDM/SI routing, MURAM parameter RAM, DMA buffer descriptor rings, NAPI processing, generic HDLC netdev operations, and suspend/resume state restoration.

Important APIs, types, and functions: major functions are `uhdlc_init()`, `ucc_hdlc_tx()`, `hdlc_tx_done()`, `hdlc_rx_done()`, `ucc_hdlc_poll()`, `ucc_hdlc_irq_handler()`, `uhdlc_ioctl()`, `uhdlc_open()`, `uhdlc_close()`, `ucc_hdlc_attach()`, `uhdlc_suspend()`, `uhdlc_resume()`, `uhdlc_memclean()`, `hdlc_map_iomem()`, `ucc_hdlc_probe()`, and `ucc_hdlc_remove()`. It uses `utdm_primary_info` defaults and `struct ucc_hdlc_private` from the header.

Control flow: probe parses DT UCC index, clocks, register resources, optional TDM/loopback/HDLC bus flags, maps SI/SIRAM when needed, initializes hardware and descriptor rings through `uhdlc_init()`, allocates an HDLC netdev, attaches NAPI, and registers it. Open requests IRQ, issues QE init commands, enables UCC RX/TX and optional TDM port, enables NAPI, starts queue, then calls `hdlc_open()`. IRQ masks events and schedules NAPI. Poll processes TX completions and RX frames, then reenables interrupts. Close disables NAPI, gracefully stops TX/RX, disables TDM/UCC, frees IRQ, stops queue, and closes HDLC.

State and persistence: state is in allocated private memory, coherent DMA BD rings/buffers, MURAM parameter RAM, UCC registers, optional TDM mappings, SKB pointer arrays, NAPI state, and PM backup fields. No disk persistence exists. Suspend stores GUMR/GUEMR, parameter RAM, and clock mux registers; resume restores them and rebuilds descriptors.

Dependencies and integration points: depends on QUICC Engine APIs (`qe_issue_cmd`, `qe_muram_alloc`, `ucc_fast_init`, `ucc_tdm_init`), OF platform parsing, DMA coherent allocation, generic HDLC, NAPI, netdevice queue accounting, and optional PM.

Risks: cleanup is complex; `ucc_hdlc_remove()` does not unregister/free the netdev in the visible code before freeing private state, which is a notable lifecycle risk if not handled elsewhere. `uhdlc_init()` allocates `riptr`/`tiptr` local MURAM offsets but only stores them in parameter RAM for later cleanup. RX allocation failure in `hdlc_rx_done()` returns before recycling the current BD. Probe has multiple mappings and allocations with different cleanup labels. PM resume rebuilds rings and can lose in-flight packets.

Test signals: DT probe for valid/invalid UCC numbers and clocks, TDM and non-TDM modes, loopback and HDLC bus modes, open/close cycles, NAPI RX/TX under load, raw/PPP/Ethernet packet paths, parity/encoding attach validation, RX BD error counters, TX underrun/carrier restart, suspend/resume while interface is running, and remove/unbind leak tests.
