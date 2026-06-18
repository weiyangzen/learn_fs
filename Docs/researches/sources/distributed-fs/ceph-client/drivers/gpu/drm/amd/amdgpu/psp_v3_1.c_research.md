# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/psp_v3_1.c

Purpose: implements the older PSP v3.1 backend for Vega10/Vega12-era devices. It loads SOS/ASD firmware, boots system and secure OS drivers, reroutes interrupt handler clients, manages PF/VF PSP rings, supports an SMU reload quirk, and implements mode1 reset.

Important APIs/types/functions: key callbacks are `psp_v3_1_init_microcode()`, `psp_v3_1_bootloader_load_sysdrv()`, `psp_v3_1_bootloader_load_sos()`, `psp_v3_1_reroute_ih()`, `psp_v3_1_ring_create()`, `psp_v3_1_ring_stop()`, `psp_v3_1_ring_destroy()`, `psp_v3_1_smu_reload_quirk()`, `psp_v3_1_mode1_reset()`, `psp_v3_1_ring_get_wptr()`, and `psp_v3_1_ring_set_wptr()`. `psp_v3_1_set_psp_funcs()` installs the table.

Control flow: initialization loads SOS then ASD microcode. Bootloader loaders skip if `C2PMSG_81` sign-of-life is set, wait on `C2PMSG_35`, copy firmware, pass the shifted primary firmware address, issue `PSP_BL__LOAD_SYSDRV` or `PSP_BL__LOAD_SOSDRV`, delay, and wait for completion/sign-of-life change. Ring creation first reroutes IH settings for VMC and UMC by writing `IH_CLIENT_CFG_DATA` through PSP mailbox commands, then follows either VF `C2PMSG_101/102/103` or PF `C2PMSG_64/69/70/71` ring setup. Mode1 reset waits for PSP ready, sends reset command, then waits for `C2PMSG_33` response.

State and persistence behavior: persistent state includes firmware descriptors, `psp->km_ring`, `adev->firmware.rbuf`, and the PSP-programmed IH routing. VF write pointer is mirrored in `psp->km_ring.ring_wptr`; PF write pointer is `C2PMSG_67`. The SMU reload quirk reads MP1 firmware flags through PCIe/SMN space and returns whether interrupts are enabled.

Dependencies and integration points: depends on MP9, GC9, SDMA, NBIO, and OSS register headers, common PSP firmware helpers, SOC15 mailbox access, SR-IOV detection, and AMDGPU reset/SMU interaction.

Risks and test signals: risks include IH reroute command failures being ignored, stale sign-of-life causing skipped firmware reload, SR-IOV ring command differences, mode1 reset timeout, and SMN address assumptions in the SMU reload quirk. Test signals include Vega10/Vega12 firmware load, PSP ring command submission, VMC/UMC interrupt routing, VF write-pointer notification, mode1 reset success, and SMU reload behavior after reset.
