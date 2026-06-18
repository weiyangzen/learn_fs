# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_10_0_offset.h

Purpose: generated AMD MP 10.0 register-offset header for MP0 and MP1 SMN mailbox access. It maps symbolic `mmMP*_SMN_*` names to SOC15-style register indices so PSP and SMU code can address firmware mailbox registers without hard-coded numeric offsets.

Important APIs and state: the interface is a macro table. MP0 `C2PMSG_32..103` occupy `0x0060..0x00a7`; MP0 `IH_CREDIT`, `IH_SW_INT`, and `IH_SW_INT_CTRL` are `0x00c1..0x00c3`. MP1 mirrors the mailbox range at `0x0260..0x02a7`, then defines `IH_CREDIT`, `IH_SW_INT`, `IH_SW_INT_CTRL`, and `FPS_CNT` at `0x02c1..0x02c4`. Every register has a companion `_BASE_IDX` macro with value `0`, indicating the register belongs to base aperture 0 for the SOC15 access helpers.

Control flow: none in the header itself. Runtime control flow appears in consumers such as `psp_v10_0.c`, which writes MP0 C2P mailbox registers to initialize PSP rings and poll firmware responses, and SMU paths that configure `msg_reg`, `resp_reg`, and argument registers through `SOC15_REG_OFFSET(MP1, 0, mmMP1_SMN_C2PMSG_*)`.

State and persistence: the macros do not hold state. They name hardware-backed registers whose contents persist in the device until reset or firmware/driver writes. C2P registers are command and argument mailboxes, interrupt registers carry software interrupt mask/ack state, and `FPS_CNT` is a counter-style MP1 register. Any software cache of values must be maintained by the caller, not inferred from this header.

Dependencies and integration: protected by `_mp_10_0_OFFSET_HEADER` and paired with `mp_10_0_default.h` and `mp_10_0_sh_mask.h`. It is included by `amdgpu/psp_v10_0.c` and by `pm/powerplay/hwmgr/smu10_inc.h`. The values are consumed by AMDGPU register helpers such as `RREG32_SOC15`, `WREG32_SOC15`, and `SOC15_REG_OFFSET`, which apply the block instance and base-index metadata.

Risks and test signals: wrong offsets can brick early PSP/SMU handshakes by sending ring addresses or commands to the wrong mailbox. MP0 and MP1 names are similar but target different firmware engines, so copy/paste mistakes are high impact. Compile tests catch missing macros; real validation requires MP 10.0 boot, PSP ring setup, SMU message-response traffic, interrupt mask/ack paths, and checks that polling loops do not timeout on C2P/P2C responses.
