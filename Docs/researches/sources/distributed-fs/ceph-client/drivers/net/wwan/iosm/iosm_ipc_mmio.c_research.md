# sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_mmio.c

Purpose: maps the CP scratchpad MMIO layout into helper functions for execution stage, chip info, ROM exit code, PSI address/size, IPC status, context info, CP version, and CP capabilities.

Important functions: `ipc_mmio_init`, `ipc_mmio_get_exec_stage`, `ipc_mmio_get_ipc_state`, `ipc_mmio_get_rom_exit_code`, `ipc_mmio_copy_chip_info`, `ipc_mmio_config`, `ipc_mmio_set_psi_addr_and_size`, `ipc_mmio_set_contex_info_addr`, `ipc_mmio_get_cp_version`, and `ipc_mmio_update_cp_capability`.

Control flow: initialization polls until CP writes a valid execution stage, validates fixed chip-info size, stores register offsets, and returns a small state object. Runtime boot writes PSI DMA address/size and later writes context-info/AP window registers during IPC init. Capability update reads CP version and capability bits to select MUX Lite vs aggregation and UL credit support.

State/dependencies: keeps base MMIO pointer, offsets, chip info metadata, context info physical address, mux protocol, and capability flags. Dependencies include Linux IO accessors, 64-bit nonatomic IO helpers, device logging, and mux capability constants. Risks: hard-coded offsets and chip-info size must match firmware; polling uses a 50*20ms bound; no locking around capability fields; CP version `0xffffffff` is treated by callers. Test signals: invalid exec stage timeout, unexpected chip info rejection, endian/64-bit writes for context/PSI, capability matrix tests, and null-pointer getter behavior.
