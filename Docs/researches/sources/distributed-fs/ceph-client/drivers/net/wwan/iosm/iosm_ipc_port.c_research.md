# sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_port.c

Purpose: bridges IOSM control channels into the Linux WWAN port subsystem for AT/MBIM/RPC-style control communication.

Important functions: `ipc_port_init`, `ipc_port_deinit`, and WWAN port ops `ipc_port_ctrl_start`, `ipc_port_ctrl_stop`, `ipc_port_ctrl_tx`. The ops open/close imem control channels and route TX SKBs through `ipc_imem_sys_cdev_write`.

Control flow: runtime worker calls `ipc_port_init` for each configured control channel with a non-unknown WWAN port type. WWAN core calls `.start`, which opens a control channel using the configured channel ID and HP update identifier; `.tx` writes SKBs to CP; `.stop` closes the channel. Deinit removes all created WWAN ports and frees the per-port structures.

State/dependencies: `iosm_cdev` stores WWAN port pointer, imem, PCIe, device, port type, channel, and channel ID. Dependencies include channel config, imem ops, WWAN framework, and SKB ownership conventions. Risks: `wwan_create_port` result is not checked before returning the allocated wrapper, stop assumes a valid channel, and deinit iterates a fixed max-channel array. Test signals: port creation failure handling, open refused outside RUN phase, TX failure SKB ownership, close with pending TDs, and device-specific skipped port types from the imem runtime worker.
