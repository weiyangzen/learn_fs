# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/psp_v14_0.c

Purpose: implements PSP v14 callbacks for MPASP-based 14.0.2/14.0.3/14.0.5 devices. It handles SOS or TOC firmware initialization, bootloader components including RAS/IP key manager drivers, ring management, memory training, USB-C PD firmware operations, and SPI ROM update/status.

Important APIs/types/functions: key callbacks are `psp_v14_0_init_microcode()`, `psp_v14_0_wait_for_bootloader()`, `psp_v14_0_bootloader_load_kdb/spl/sysdrv/soc_drv/intf_drv/dbg_drv/ras_drv/ipkeymgr_drv/sos()`, `psp_v14_0_ring_create/stop/destroy()`, `psp_v14_0_memory_training()`, `psp_v14_0_load_usbc_pd_fw()`, `psp_v14_0_read_usbc_pd_fw()`, `psp_v14_0_update_spirom()`, and `psp_v14_0_vbflash_status()`.

Control flow: microcode initialization loads SOS/TA for 14.0.2 and 14.0.3, or TOC/TA for 14.0.5. Bootloader component load is v13-like but uses `regMPASP_SMN_C2PMSG_*` registers; debug driver load maps to the v14-renamed HAD driver command. Ring create/stop branches for SR-IOV VF GPCOM versus PF rings. Memory training mirrors v13 behavior with MPASP mailbox registers. USB-C PD load passes a shifted LFB address, waits for readiness, sends `GFX_CMD_USB_PD_USE_LFB`, and polls up to 240 seconds. SPI update writes low/high firmware address words and runs update commands through `C2PMSG_115/116` plus doorbell `C2PMSG_73`.

State and persistence behavior: state lives in PSP firmware descriptors, the primary firmware buffer, `psp->km_ring`, memory-training context, and `psp->vbflash_done`. Mailbox state is maintained in MPASP C2PMSG registers. No SPI dump or RAS capability callback is provided in this file.

Dependencies and integration points: depends on MP 14.0.2 register definitions, common PSP helpers, SR-IOV detection, VRAM access and HDP flush for memory training, USB-C PD firmware support, VBIOS flashing, and the common PSP function table.

Risks and test signals: risks include register namespace changes from MP0 to MPASP, a double wait in `psp_v14_0_exec_spi_cmd()` after the conditional SPI update wait, long USB-C and SPI timeouts, bootloader component ordering, and memory-training VRAM preservation. Test signals include firmware load on all supported v14 versions, PF/VF ring command submission, memory-training long and short flows, USB-C PD load/version paths, VBIOS flash update and status, and bootloader HAD/RAS/IP-key-manager component loads.
