# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_vdec0_brdg_ctrl_axuser_msix_abnrm_regs.h

Purpose: generated AXUSER map for the abnormal MSI-X path of `DCORE0_VDEC0_BRDG_CTRL`. It exports 19 `mmDCORE0_VDEC0_BRDG_CTRL_AXUSER_MSIX_ABNRM_*` constants from `0x41E3B00` to `0x41E3B4C`.

Important APIs/types/functions: no functions/types. Macros cover the same HB/LB AXUSER attribute and override fields as other bridge AXUSER maps, scoped to abnormal MSI-X notifications.

Control flow: none. Interrupt/bridge initialization code programs these registers so abnormal interrupt writes use the intended transaction attributes.

State and persistence behavior: persistent transaction attribute state for abnormal MSI-X writes. Misprogramming affects interrupt write routing, protection, and ordering.

Dependencies and integration points: included by `gaudi2_regs.h`; semantically tied to ABNRM interrupt mask/wait/counter registers in `dcore0_vdec0_brdg_ctrl_regs.h` and corresponding mask definitions.

Risks: wrong attributes can lose or misroute abnormal event MSI-X writes. Security-sensitive fields such as ASID and MMU bypass must match the interrupt delivery design.

Test signals: abnormal interrupt injection tests, MSI-X delivery/readback tests, AXI violation monitoring, and generated map validation against VDEC bridge spec.
