<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pcie_wrap_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pcie_wrap_regs.h

## Purpose
`pcie_wrap_regs.h` defines the Gaudi2 PCIe wrapper register block around the PCIe controller. It covers MSI/MSI-X gatewaying, virtual UART, host access termination, LBW gateways, transaction metadata capture/override, MESO FIFO diagnostics, peer-to-peer tables, reset/hot-reset controls, AXI split/drain controls, PHY/core base addresses, interrupt indications, PMMU routing, ASID modification, CoreSight trace AXI control, and external-memory location mapping.

## Important APIs, types, and functions
The file exports `mmPCIE_WRAP_*` macros. Key groups include interrupt generator mask ranges and timer/control, MSI-X doorbell/mask/gateway/vector/table registers, VUART RX/TX, illegal LBW request capture, outbound address, LBW gateway address/data/go/status arrays, slave AW/AR misc TLP metadata, MESO FIFO counters/LFSR/backpressure controls, P2P table 0-63 plus enable/request/interrupt/terminate controls, CPU hot reset, PCIe cache/lock/prot/user overrides, outstanding/inflight controls, AXI split interrupts and drain controls, PHY/core base addresses, SPMU/AXI/IC interrupt indicators, PMMU router config, PSOC reset/boot done, ASID modification, FLR FSM control, drain address stamps, and external memory HBM/PC mapping.

## Control flow
No executable code is present. Probe/reset paths configure MSI-X gatewaying, outbound/LBW access, P2P routing, and reset controls. Error paths read illegal request, AXI split, drain, and interrupt indicator registers. Reset/quiesce flows use drain active/timeout/config and FLR FSM controls to stop traffic before reset.

## State and persistence
Wrapper state includes interrupt gateway tables, VUART data, captured illegal transaction state, P2P mappings, AXI override policy, drain status, ASID modification windows, and external-memory location maps. Most state must be rebuilt after FLR or device reset.

## Dependencies and integration points
Included by `gaudi2_regs.h`, it complements `pcie_aux_regs.h`, `pcie_dbi_regs.h`, PCIe VDEC bridge files, interrupt setup, firmware boot management, and memory-routing/security code.

## Risks and test signals
Incorrect wrapper programming can break MSI-X, host MMIO access, P2P transactions, reset drain, or security metadata. Test signals include MSI-X vector delivery, VUART operation if used, illegal LBW request capture on injection, P2P table behavior, successful FLR/hot reset, drain completion before reset, and no stale ASID/AXUSER overrides after reinit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pcie_wrap_regs.h -->
