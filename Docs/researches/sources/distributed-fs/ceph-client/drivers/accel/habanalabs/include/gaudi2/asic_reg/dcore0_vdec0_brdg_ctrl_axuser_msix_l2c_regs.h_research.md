# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_vdec0_brdg_ctrl_axuser_msix_l2c_regs.h

Purpose: generated AXUSER register map for the L2C MSI-X path of the VDEC0 bridge. It exports 19 `mmDCORE0_VDEC0_BRDG_CTRL_AXUSER_MSIX_L2C_*` constants from `0x41E3900` to `0x41E394C`.

Important APIs/types/functions: macro-only API for HB ASID/MMU bypass/order/snoop/reduction/atomic/QoS/reserved/core/emem fields, E2E coordination, and HB/LB override registers for L2C MSI-X traffic.

Control flow: none. External interrupt bridge setup uses these constants to program attributes for L2C-originated MSI-X writes.

State and persistence behavior: hardware transaction attributes persist and govern L2C MSI-X write behavior.

Dependencies and integration points: included by `gaudi2_regs.h`; linked to L2C GIC/MSI-X mask, wait counter, APB write, completion queue, and MSI-X LBW address/data registers in `dcore0_vdec0_brdg_ctrl_regs.h`.

Risks: misconfigured L2C MSI-X attributes can cause lost interrupts, invalid memory writes, or isolation breaches.

Test signals: L2C interrupt delivery tests, bridge status/counter readbacks, AXUSER initialization checks, and generated address validation.
