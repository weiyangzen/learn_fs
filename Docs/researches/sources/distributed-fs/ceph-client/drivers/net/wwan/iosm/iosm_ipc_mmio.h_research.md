# sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_mmio.h

Purpose: defines the IOSM scratchpad ABI exposed by CP firmware: IPC states, ROM exit codes, execution-stage magic values, MMIO offset storage, capability masks, and the `iosm_mmio` state object.

Important types/APIs: `ipc_mem_device_ipc_state`, `rom_exit_code`, `ipc_mem_exec_stage`, `mmio_offset`, `iosm_mmio`, and prototypes for MMIO init, PSI/context writes, state getters, chip-info copy, configuration, and capability refresh. Capability masks `DL_AGGR`, `UL_AGGR`, and `UL_FLOW_CREDIT` control mux selection and credit mode.

Control flow role: imem maps execution-stage magic values to AP phases; flash uses ROM/PSI/EBL/RUN gating; protocol writes context info; imem ops perform PSI boot handoff through address/size registers. State is volatile MMIO plus cached capability metadata.

Dependencies: requires Linux types such as `dma_addr_t`, `phys_addr_t`, `size_t`, `u32`, `BIT`, and `struct device` from include context. Risks include treating firmware magic constants as stable ABI, unexpected CP capability versions, and offset mismatches. Test signals: compile include checks, mapping every execution stage to phase behavior, null-safe getters, and capability parsing for old and new CP versions.
