# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/firmware.c

## Purpose
`firmware.c` manages Venus firmware loading, secure/non-secure boot, firmware memory mapping, CPU reset control, content-protection memory programming, firmware-version validation, and firmware device/IOMMU setup.

## Important APIs And Functions
- Hardware state/reset: `venus_reset_cpu()`, `venus_set_hw_state()`.
- Firmware image handling: `venus_load_fw()`, `venus_boot()`, `venus_shutdown()`.
- Non-TrustZone boot path: `venus_boot_no_tz()`, `venus_shutdown_no_tz()`.
- Platform quirks and validation: `venus_firmware_cfg()`, `venus_firmware_check()`.
- Firmware child device lifecycle: `venus_firmware_init()`, `venus_firmware_deinit()`.

## Control Flow
`venus_firmware_init()` looks for a `video-firmware` child node. If absent, the driver uses the TrustZone/PAS path. If present, it registers a child platform device, configures DMA, allocates an IOMMU paging domain, attaches the device, and stores the firmware device/domain in `core->fw`.

`venus_boot()` verifies MDT loader availability and SCM availability for secure boot, chooses firmware name from `firmware-name` DT property or SoC resource data, loads the MDT into reserved memory via `venus_load_fw()`, records physical address and size, then either authenticates/resets the PAS image through SCM or maps the firmware memory at IOVA 0 and releases the local CPU reset. Secure boot may also program video content-protection address ranges via `qcom_scm_mem_protect_video_var()`.

Shutdown mirrors the boot mode: secure boot uses `qcom_scm_pas_shutdown()`, while non-secure boot asserts CPU reset and unmaps the IOMMU firmware region. Firmware check compares `core->venus_ver` against an optional resource minimum.

## State And Persistence
- Mutates `core->use_tz` and `core->fw` fields: child device, IOMMU domain, mapped memory size, physical firmware memory, and memory size.
- Writes wrapper registers for firmware start/end, CPA/non-pixel ranges, CPU clock/reset, and XTSS/A9SS reset.
- No persistent files are written; firmware version is parsed elsewhere and checked here.

## Dependencies And Integration Points
- Linux firmware, reserved-memory, platform-device, DMA, IOMMU, and MMIO APIs.
- Qualcomm SCM and MDT loader APIs.
- Register definitions from `hfi_venus_io.h` and version macros from `core.h`.
- `core.c` calls init, boot, cfg, check, shutdown, and deinit in probe/remove/recovery.

## Risks And Edge Cases
- Reserved memory must exist and be large enough for the MDT image but not exceed `VENUS_FW_MEM_SIZE`; otherwise boot fails.
- Non-secure boot depends on a correctly described `video-firmware` child and IOMMU attachment; failures cause probe deferral or error.
- Secure boot requires SCM availability; otherwise boot defers.
- `venus_shutdown_no_tz()` reports unmap-size mismatch but still returns `0`, so partial cleanup relies on logs.
- Firmware version check requires `core->venus_ver` to have been populated by HFI image-version handling before validation.

## Test Signals
- Probe should request and load the expected firmware path for each compatible SoC.
- Secure devices should authenticate/reset via PAS and program CP ranges when configured.
- Non-secure devices should attach IOMMU, map IOVA 0, release reset, and unmap on shutdown.
- Firmware minimum-version tests should reject old qcm2290 images with the logged version comparison.
