# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/psp_v15_0.c

Purpose: implements PSP 15.0.0 callbacks for a TOC/TA firmware backend with PSP ring management. It is minimal compared with v13/v14 and primarily handles firmware table setup and ring mailbox differences for PF versus SR-IOV.

Important APIs/types/functions: callbacks are named `psp_v15_0_0_init_microcode()`, `psp_v15_0_0_ring_stop()`, `psp_v15_0_0_ring_create()`, `psp_v15_0_0_ring_destroy()`, `psp_v15_0_0_ring_get_wptr()`, and `psp_v15_0_0_ring_set_wptr()`. `psp_v15_0_0_set_psp_funcs()` installs `psp_v15_0_0_funcs`.

Control flow: initialization decodes the MP0 firmware prefix, loads TOC microcode, then loads TA microcode. Ring stop and create branch on SR-IOV. VF mode uses `regMPASP_SMN_C2PMSG_101/102/103`; PF mode uses the PCRU1 MPASP register aliases for `C2PMSG_64/67/69/70/71`. Ring creation waits for ready, writes ring address and size, sends the shifted ring type, delays, and waits for response. Destroy stops the ring and frees `adev->firmware.rbuf`.

State and persistence behavior: persistent PSP state is `psp->funcs`, firmware descriptors populated by common PSP helpers, and `psp->km_ring`. PF write pointer is in `regMPASP_PCRU1_MPASP_C2PMSG_67`; VF write pointer is in `regMPASP_SMN_C2PMSG_102`.

Dependencies and integration points: depends on MP 15.0.0 register headers, common PSP firmware helpers, SR-IOV detection, and AMDGPU IP discovery selecting the v15.0.0 backend.

Risks and test signals: risks include register alias misuse between PF and VF paths, copied error text naming v14 in v15 failures, mailbox mask changes, and absent bootloader/memory-training callbacks. Test signals include TOC/TA firmware load, PF and VF PSP ring command submission, write-pointer updates, and teardown after reset or driver unload.
