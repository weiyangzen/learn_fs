<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soundwire/sdw_amd.h -->
# sources/distributed-fs/ceph-client/include/linux/soundwire/sdw_amd.h

Purpose: This header defines the AMD SoundWire manager integration contract, including ACP resource descriptions, manager state, ACPI scan results, and probe/exit APIs.

Important APIs/types/functions: `acp_sdw_pdata` carries instance, ACP revision, and a shared ACP register mutex. `sdw_amd_dai_runtime` links DAI names to SoundWire streams. `amd_sdw_manager` embeds `sdw_bus`, MMIO bases, work items, status array, port/frame-shape fields, quirks, wake mask, power mode mask, clock-stopped flag, and DAI runtime array. `sdw_amd_res` and `sdw_amd_ctx` describe global resources and probe context. APIs are `sdw_amd_probe()`, `sdw_amd_exit()`, `sdw_amd_get_slave_info()`, and `amd_sdw_scan_controller()`.

Control flow: Parent audio/DSP code scans ACPI, prepares `sdw_amd_res`, probes managers, retrieves slave information, and exits through the context. Runtime work is split between IRQ/status workqueues and shared ACP register locking.

State and persistence: Manager state persists per link. `clk_stopped` and `power_mode_mask` drive suspend behavior: clock-stop mode keeps bus context, while power-off mode requires reset and re-enumeration.

Dependencies/integration: Depends on ACPI, platform devices, SoundWire core, workqueues, MMIO, and ACP shared register locking. Revision constants identify ACP63/70/71/72 variants.

Risks and test signals: Risks include missing ACP lock coverage, wrong link mask/count, power-mode wake limitations, stale port offset maps, and re-enumeration after power-off. Test via ACPI scan results, two-manager systems, suspend/runtime suspend, wake masks, IRQ work execution, and slave-info population.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soundwire/sdw_amd.h -->
