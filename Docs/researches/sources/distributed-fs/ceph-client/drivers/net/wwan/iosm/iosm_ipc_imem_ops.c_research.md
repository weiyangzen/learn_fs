# sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_imem_ops.c

Purpose: provides the system-facing operations that WWAN netdevs, WWAN control ports, and devlink flashing/coredump paths use to open channels, write uplink data, close channels, and read downlink SIO data.

Important functions: `ipc_imem_sys_wwan_open/close/transmit`, `ipc_imem_wwan_channel_init`, `ipc_imem_sys_port_open/close`, `ipc_imem_sys_cdev_write`, `ipc_imem_sys_devlink_open/close/read/write/notify_rx`, and internal PSI transfer/DMA mapping helpers.

Control flow: WWAN open validates RUN phase then delegates to mux session open; transmit routes SKBs into mux encoding. Port open reserves and opens a control channel; writes DMA-map SKBs, queue them on the channel UL list, and schedule imem UL send. Devlink open has phase-specific behavior: in ROM/OFF it reserves the flash channel and enqueues chip info; in PSI/EBL it opens the real pipes. ROM writes perform PSI transfer through MMIO scratchpad and doorbell; later writes allocate DMA SKBs and block until CP consumes them. Reads wait on `read_sem` and copy queued SKBs.

State/dependencies: uses imem channel state, mux sessions, devlink SIO queues, completions, PCIe DMA helpers, MMIO execution/IP state, and protocol head/tail queries. Risks include blocking waits in close/write/read paths, ROM/PSI phase coupling, `nr_of_channels--` in devlink close, SKB ownership on failed writes, and timeout-dependent boot behavior. Test signals: phase rejection, DMA map failure, read timeout/short destination, pending TD close waits, PSI ROM exit codes, and mux aggregation channel sizing.
