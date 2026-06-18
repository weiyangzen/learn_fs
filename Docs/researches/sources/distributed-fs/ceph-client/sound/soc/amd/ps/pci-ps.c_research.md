# sources/distributed-fs/ceph-client/sound/soc/amd/ps/pci-ps.c

## Purpose
This is the PCI parent driver for AMD ACP6.3, ACP7.0, ACP7.1, and ACP7.2 platforms. It owns the PCI BAR mapping, revision dispatch, top-level ACP initialization, interrupt dispatch, SoundWire discovery, PDM/DMIC platform-device creation, SoundWire DMA platform-device creation, and machine-driver registration.

## Important APIs, Types, And Functions
The central state is `struct acp63_dev_data`, allocated in `snd_acp63_probe()` and stored with `pci_set_drvdata()`. Probe uses `snd_amd_acp_find_config()`, `acp_hw_init_ops()`, `acp_hw_init()`, `get_acp63_device_config()`, `create_acp63_platform_devs()`, and `acp63_machine_register()`. IRQ entry points are `acp63_irq_handler()` and threaded `acp63_irq_thread()`. SoundWire-specific helpers include `acp_scan_sdw_devices()`, `amd_sdw_probe()`, `amd_sdw_exit()`, and `acp63_sdw_machine_select()`.

## Control Flow
Probe rejects non-ACP6.3/7.x revisions and configurations claimed by other AMD audio stacks, enables PCI, maps BAR0, initializes revision-specific hardware ops, requests a shared threaded IRQ, discovers PDM and SoundWire availability from ACP pin config, ACPI DMIC properties, `_WOV`, and SoundWire ACPI scan results, then registers platform children. PDM creates `acp_ps_pdm_dma` and `dmic-codec`; SoundWire calls `sdw_amd_probe()` then creates `amd_ps_sdw_dma`; a machine device is registered for either SoundWire match data or the local PDM machine. Remove reverses SoundWire, PDM, machine, hardware, runtime PM, PCI regions, and PCI enable state.

## State And Persistence Behavior
Persistent runtime state lives in `acp63_dev_data`: MMIO base, PCI revision, platform devices, ACP lock, subsystem IDs, PDM/SoundWire capability flags, SoundWire machine table, wake-event latches, and DMA interrupt status arrays. The IRQ handler acknowledges hardware status bits by writing the same bit back, records SoundWire DMA stream interrupt flags, and defers period-elapsed calls to the threaded handler through `acp_hw_sdw_dma_irq_thread()`. Runtime/system PM delegates to revision-specific ops through `acp_hw_suspend()`, `acp_hw_runtime_resume()`, and `acp_hw_resume()`.

## Dependencies And Integration Points
The driver integrates with Linux PCI, platform devices, runtime PM, ACPI, ASoC machine selection, AMD SoundWire core (`sdw_amd_probe`, `sdw_amd_exit`, `amd_sdw_scan_controller`), and AMD machine tables from `mach-config.h`. It depends on `acp63.h` for register offsets, revisions, masks, platform-data fields, and helper wrappers implemented in `ps-common.c`.

## Risks And Edge Cases
The probe intentionally continues if no PDM or SoundWire device is found, leaving only the initialized PCI device and PM state. IRQ handling assumes child platform devices and SoundWire manager platform devices exist before matching interrupt bits are delivered; malformed firmware could expose null paths. ACP70 wake handling uses per-manager latches and `pm_request_resume()`, so wake regression tests should include suspended SoundWire links. Error IRQ handling clears error registers but does not report per-manager SoundWire error details.

## Test Signals
Useful signals are successful module bind for PCI device `0x15e2` with expected revisions, child platform devices under `/sys/bus/platform/devices`, `dmesg` errors from platform registration paths, SoundWire machine selection logs with SSID, PDM capture period interrupts, SoundWire playback/capture period interrupts, and suspend/resume with SoundWire wake events. Kconfig coverage should include both `CONFIG_SND_SOC_AMD_SOUNDWIRE=y/m` and disabled SoundWire builds because this file has compiled stubs.
