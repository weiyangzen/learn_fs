<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_acp.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_acp.c

## Purpose
`amdgpu_acp.c` implements the amdgpu IP block for the AMD Audio Co-Processor 2.x. It initializes ACP software state, powers and resets ACP hardware, registers MFD child devices for the ACP DMA and DesignWare I2S controllers, wires children into a generic PM domain, handles board-specific I2S resource layout quirks, and exposes the `acp_ip_block` version descriptor to the amdgpu IP manager.

## Important APIs, types, and functions
- `acp_sw_init()` creates the CGS device used for ACP register access and stores `adev->acp.parent`.
- `acp_sw_fini()` destroys the CGS device.
- `struct acp_pm_domain` wraps a generic PM domain and back pointer to `amdgpu_device`.
- `acp_poweroff()` and `acp_poweron()` call SMU power-gating helpers to gate/ungate the ACP block for PM-domain transitions.
- `acp_hw_init()` calls `amd_acp_hw_init()`, allocates `acp_genpd`, MFD cells, resources, and I2S platform data, registers child devices, adds them to the PM domain, performs ACP soft reset, enables ACP clock, and deasserts reset.
- `acp_hw_fini()` asserts soft reset, disables clock, removes children from genpd, removes MFD devices, and frees allocated resources.
- `acp_suspend()` and `acp_resume()` manage power gating for systems where no ACP child cell was registered.
- `acp_set_powergating_state()` gates or ungates ACP through SMU.
- `acp_ip_funcs` and `acp_ip_block` expose the AMD IP block callbacks and version 2.2 descriptor.

## Control flow
The amdgpu IP manager calls `sw_init` first, creating the CGS device. Hardware init then calls `amd_acp_hw_init()`. If it returns `-ENODEV`, the board uses AZ audio rather than ACP, so ACP is power-gated and init succeeds with no child devices. Otherwise, the function validates MMIO size, creates the PM domain, checks DMI quirks, and branches on `acp_machine_id`.

For `ST_JADEITE`, the file creates two MFD cells: `acp_audio_dma` and a combined playback/capture `designware-i2s` child, with three resources. For the default path, it creates four MFD cells: DMA plus separate playback, capture, and Bluetooth I2S controllers, with five resources. Stoney ASICs receive I2S quirks for 16-bit index override and capture comp-param handling.

After child registration, the code asserts ACP soft reset and polls for `SoftResetAudDone`, enables ACP clock and polls `mmACP_STATUS`, then deasserts soft reset. Failure paths free allocated arrays and return the error. Hardware fini mirrors reset/clock operations, removes PM-domain attachments, removes MFD children, and frees resources.

## State and persistence behavior
ACP state is runtime-only and stored in `adev->acp`: parent device, CGS device, private pointer, MFD cell array, resource array, and PM domain pointer. A file-static `acp_machine_id` records DMI quirk detection during init.

The MFD child devices and PM-domain membership persist until `acp_hw_fini()`. ACP power state changes are delegated to SMU and can be triggered by IP-block power-gating callbacks or child PM-domain transitions. No persistent user data is written.

## Dependencies and integration points
The file depends on Linux platform/MFD/generic PM domain/DMI/ACPI headers, DesignWare I2S platform data, ALSA PCM rate constants, CGS register helpers, ACP GFX interface helpers, SMU power-gating through `amdgpu_dpm_set_powergating_by_smu()`, and amdgpu IRQ mapping.

It integrates with downstream audio drivers via MFD cells named `acp_audio_dma` and `designware-i2s`; with runtime PM through `generic_pm_domain`; and with amdgpu IP-block lifecycle through `acp_ip_block`.

## Risks and edge cases
The allocation failure path frees `i2s_pdata`, `acp_res`, `acp_cell`, and `acp_genpd`, but `i2s_pdata` is only owned through MFD platform data after successful `mfd_add_devices()`. Lifetime must stay compatible with child device expectations. The default path allocates `i2s_pdata` locally and does not explicitly free it on normal `hw_fini`, so ownership/lifetime is subtle.

The clock-disable poll in `acp_hw_fini()` checks for `val & 0x1`, the same condition as enable, which may be hardware-specific but is suspicious and should be tested against real ACP status semantics. MMIO-size validation uses a fixed threshold. Board quirks depend on exact DMI strings and leave `acp_machine_id` static for future init calls.

## Test signals
Good signals include successful ACP audio playback/capture on default and Jadeite/ASN boards, correct MFD child creation, child removal without leaks or use-after-free, PM-domain power on/off calls reaching SMU, soft reset and clock polls completing, and `-ENODEV` boards cleanly power-gating ACP without exposing children. Suspend/resume should preserve behavior both with and without registered ACP cells.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_acp.c -->
