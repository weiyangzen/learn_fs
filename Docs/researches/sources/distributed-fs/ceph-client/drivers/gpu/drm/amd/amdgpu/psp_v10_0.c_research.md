# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/psp_v10_0.c

Purpose: implements PSP function callbacks for MP0/PSP v10 Raven-family APUs. It initializes ASD and TA firmware and provides the mailbox sequence for creating, stopping, destroying, and advancing the kernel PSP ring.

Important APIs/types/functions: file-local callbacks are `psp_v10_0_init_microcode()`, `psp_v10_0_ring_create()`, `psp_v10_0_ring_stop()`, `psp_v10_0_ring_destroy()`, `psp_v10_0_mode1_reset()`, `psp_v10_0_ring_get_wptr()`, and `psp_v10_0_ring_set_wptr()`. `psp_v10_0_funcs` installs those callbacks through exported `psp_v10_0_set_psp_funcs()`. Firmware declarations cover Raven, Picasso, and Raven2 ASD/TA blobs.

Control flow: initialization decodes the MP0 firmware prefix, loads ASD, then TA microcode. A Raven GC 9.1.0 revision-specific secure-display workaround zeroes the secure display TA size for firmware versions at or above `0x27000008`. Ring creation writes the ring GPU address low/high and size to `C2PMSG_69/70/71`, writes the ring type shifted into `C2PMSG_64`, delays 20 ms, and waits for the PSP response flag. Stop writes the destroy command to `C2PMSG_64`; destroy stops and frees `adev->firmware.rbuf`.

State and persistence behavior: persistent state is in `psp->km_ring`, `adev->firmware.rbuf`, and firmware/TA descriptors loaded by common PSP helpers. The ring write pointer is stored in hardware register `C2PMSG_67`. No mode1 reset state is supported; the callback returns `-EINVAL`.

Dependencies and integration points: depends on `amdgpu_psp` helpers, firmware naming from `amdgpu_ucode_ip_version_decode()`, SOC15 MP0 register macros, Raven GC/SDMA register headers, and the common PSP lifecycle that calls this `struct psp_funcs` table.

Risks and test signals: risks include mailbox timeout, incorrect ring address alignment, the fixed 20 ms handshake delay masking races, failure to free the ring buffer after partial stop failures, and the secure-display workaround being too narrow or too broad. Test signals are PSP firmware load success on Raven/Picasso/Raven2, ring command submission, write-pointer updates through `C2PMSG_67`, clean suspend/remove teardown, and explicit mode1 reset rejection.
