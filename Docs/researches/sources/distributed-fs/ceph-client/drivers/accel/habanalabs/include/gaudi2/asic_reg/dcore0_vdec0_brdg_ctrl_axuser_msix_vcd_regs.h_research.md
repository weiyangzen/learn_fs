# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_vdec0_brdg_ctrl_axuser_msix_vcd_regs.h

Purpose: generated AXUSER map for the VCD MSI-X channel of the VDEC0 bridge. It exports 19 `mmDCORE0_VDEC0_BRDG_CTRL_AXUSER_MSIX_VCD_*` constants from `0x41E3800` to `0x41E384C`.

Important APIs/types/functions: macro-only API for HB transaction attributes, E2E coordination, and HB/LB override registers for VCD MSI-X traffic.

Control flow: none. Interrupt setup code writes these registers as part of VCD MSI-X channel initialization.

State and persistence behavior: hardware AXUSER state persists and controls VCD MSI-X transaction identity/protection/order behavior.

Dependencies and integration points: included by `gaudi2_regs.h`; connected to VCD interrupt mask, flow mask, wait counters, software-register/APB write, completion queue, and MSI-X address/data registers in `dcore0_vdec0_brdg_ctrl_regs.h`.

Risks: wrong VCD MSI-X attributes can misroute interrupts or bypass intended translation/protection. Care is needed to avoid mixing VCD and other MSI-X channel address windows.

Test signals: VCD interrupt delivery tests, bridge counter/status readback, AXI violation checks, and generated register map comparison.
