# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/psp_v12_0.c

Purpose: implements PSP v12 callbacks for Renoir/Green Sardine APUs, covering ASD/TA firmware initialization, bootloader system driver and SOS loading, PSP ring management, and mode1 reset.

Important APIs/types/functions: key callbacks are `psp_v12_0_init_microcode()`, `psp_v12_0_bootloader_load_sysdrv()`, `psp_v12_0_bootloader_load_sos()`, `psp_v12_0_ring_create()`, `psp_v12_0_ring_stop()`, `psp_v12_0_ring_destroy()`, `psp_v12_0_mode1_reset()`, `psp_v12_0_ring_get_wptr()`, and `psp_v12_0_ring_set_wptr()`. `psp_v12_0_set_psp_funcs()` installs `psp_v12_0_funcs`.

Control flow: initialization loads ASD and TA microcode, then disables secure-display TA use unless the APU is Renoir. Bootloader loaders skip work when `C2PMSG_81` sign-of-life is set, otherwise wait on `C2PMSG_35`, copy firmware through `psp_copy_fw()`, provide the firmware buffer address through `C2PMSG_36`, and send v12 bootloader commands through `C2PMSG_35`. Ring create programs `C2PMSG_69/70/71` and `C2PMSG_64`; stop handles both VF GPCOM and PF ring destroy paths. Mode1 reset waits for PSP ready, sends `GFX_CTRL_CMD_ID_MODE1_RST`, sleeps, and verifies `C2PMSG_33` response.

State and persistence behavior: firmware descriptors, secure-display context, ring buffer, and mailbox state are persistent across the PSP lifecycle. VF write pointers are held in `C2PMSG_102`, PF write pointers in `C2PMSG_67`.

Dependencies and integration points: depends on common PSP firmware helpers, Renoir/Green Sardine firmware names, SOC15 MP12 register definitions, SR-IOV detection, and AMDGPU reset paths.

Risks and test signals: risks include secure-display gating errors, using hard-coded shifted bootloader command values, missing delay behavior compared with v11, and mailbox timeouts in mode1 reset. Test signals are Renoir and Green Sardine firmware load, secure-display availability only on Renoir, PF/VF ring operation, bootloader SOS/sysdrv path after cold boot, and mode1 reset success/failure logs.
