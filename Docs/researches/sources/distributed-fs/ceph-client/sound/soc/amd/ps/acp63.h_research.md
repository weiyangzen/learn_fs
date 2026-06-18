# sources/distributed-fs/ceph-client/sound/soc/amd/ps/acp63.h

## Purpose
`ps/acp63.h` is the shared private interface for the AMD Pink Sardine ACP PCI, PDM DMA, SoundWire DMA, machine, and hardware-callback code. Despite the filename, it covers ACP6.3, ACP7.0, ACP7.1, and ACP7.2 style platforms. It centralizes device IDs, register range constants, power/reset/status masks, DMA buffer geometry, PDM and SoundWire memory-window layout, interrupt bit mappings, stream enums, runtime data structures, hardware operation callbacks, inline dispatcher helpers, and the exported configuration lookup prototype.

This file is active in the PS driver path: `pci-ps.c`, `ps-common.c`, `ps-pdm-dma.c`, `ps-sdw-dma.c`, and `ps-mach.c` include it.

## Important APIs, types, and constants
Platform identity and register geometry:

- `ACP_DEVICE_ID` is `0x15E2`.
- `ACP63_REG_START`/`ACP63_REG_END` define the MMIO register window range used when registering child platform resources.
- `ACP63_PCI_REV`, `ACP70_PCI_REV`, `ACP71_PCI_REV`, and `ACP72_PCI_REV` select generation-specific hardware ops and DMA interrupt mappings.

Power, reset, timing, and status constants:

- `ACP_SOFT_RESET_SOFTRESET_AUDDONE_MASK`, `ACP63_PGFSM_*`, `ACP70_PGFSM_*`, `ACP63_TIMEOUT`, `ACP70_TIMEOUT`, `DELAY_US`, `ACP_DELAY_US`, and `ACP_COUNTER` are used by `ps-common.c` polling flows.
- `ACP_ERROR_IRQ`, `ACP_ERROR_MASK`, `ACP_EXT_INTR_STAT_CLEAR_MASK`, `PDM_DMA_STAT`, and `PDM_DMA_INTR_MASK` describe interrupt and error handling.
- `ACP_SUSPEND_DELAY_MS` defines runtime suspend delay policy for the PCI driver.

PDM constants:

- Capture hardware limits are fixed by `CAPTURE_*`, `MAX_BUFFER`, and `MIN_BUFFER`.
- `ACP_DMIC_DEV`, `ACP63_DMIC_ADDR`, `PDM_DECIMATION_FACTOR`, `ACP_PDM_CLK_FREQ_MASK`, `ACP_WOV_GAIN_CONTROL`, `ACP_PDM_ENABLE`, `ACP_PDM_DISABLE`, and `ACP_PDM_DMA_EN_STATUS` are used by `ps-pdm-dma.c`.
- `ACP_SRAM_PTE_OFFSET`, `PDM_PTE_OFFSET`, `PDM_MEM_WINDOW_START`, and `PAGE_SIZE_4K_ENABLE` configure DMA page tables and memory windows.

SoundWire constants:

- `ACP63_SDW_ADDR`, `AMD_SDW_MAX_MANAGERS`, `ACP_SDW0_STAT`, `ACP_SDW1_STAT`, and SDW DMA IRQ masks define discovery and IRQ handling.
- `ACP63_SDW0_DMA_MAX_STREAMS`, `ACP63_SDW1_DMA_MAX_STREAMS`, `ACP70_SDW0_DMA_MAX_STREAMS`, and `ACP70_SDW1_DMA_MAX_STREAMS` size stream arrays.
- `ACP63_SDW0_DMA_TX_IRQ_MASK(i)`, `ACP63_SDW0_DMA_RX_IRQ_MASK(i)`, `ACP63_SDW1_DMA_IRQ_MASK(i)`, `ACP70_SDW0_DMA_TX_IRQ_MASK(i)`, `ACP70_SDW0_DMA_RX_IRQ_MASK(i)`, `ACP70_SDW1_DMA_TX_IRQ_MASK(i)`, and `ACP70_SDW1_DMA_RX_IRQ_MASK(i)` encode stream-id to interrupt-bit mappings.
- `SDW_PTE_OFFSET(i)`, `ACP_SDW_FIFO_OFFSET(i)`, and `SDW_MEM_WINDOW_START(i)` compute per-manager SoundWire DMA page table, FIFO, and memory window addresses.

Enums:

- `enum acp_config` enumerates BIOS pin/config values used by hardware callbacks to set `is_pdm_config` and `is_sdw_config`.
- `enum amd_acp63_sdw0_channel`, `enum amd_acp63_sdw1_channel`, and `enum amd_acp70_sdw_channel` define stream IDs for SDW DMA interrupt and runtime stream arrays.

Key structs:

- `struct pdm_stream_instance` stores per-open PDM DMA state: page count, channels, DMA address, byte count, and MMIO base.
- `struct pdm_dev_data` stores PDM component device state: IRQ flag, MMIO base, shared ACP lock pointer, and active capture substream.
- `struct sdw_dma_dev_data` stores SoundWire DMA component state: MMIO base, shared lock, ACP revision, and per-generation/per-manager substream arrays.
- `struct acp_sdw_dma_stream` stores per-open SoundWire stream state: page count, channels, stream ID, manager instance, DMA address, and byte count.
- `union acp_sdw_dma_count` provides high/low and `u64` views for byte counters.
- `struct sdw_dma_ring_buf_reg` groups register offsets needed to program one SoundWire ring buffer.
- `struct acp_hw_ops` is the platform-generation operation table for init/deinit/config/IRQ/suspend/resume callbacks.
- `struct acp63_dev_data` is the PCI driver context, tying together MMIO, resources, child platform devices, locks, SoundWire ACPI/probe context, machine tables, configuration booleans, wake flags, subsystem IDs, saved pad state, and DMA interrupt status arrays.

Inline APIs:

- `acp_hw_init()`, `acp_hw_deinit()`, `acp_hw_get_config()`, `acp_hw_sdw_dma_irq_thread()`, `acp_hw_suspend()`, `acp_hw_resume()`, `acp_hw_suspend_runtime()`, and `acp_hw_runtime_resume()` validate callback presence and dispatch through `struct acp_hw_ops`, returning `-EOPNOTSUPP` for missing integer callbacks.
- `acp63_hw_init_ops()` and `acp70_hw_init_ops()` are declared for `ps-common.c` to populate callback tables.
- `snd_amd_acp_find_config()` is declared for the shared machine-configuration lookup implemented in `acp-config.c`.

## Control flow
The header enables the following runtime flow:

1. `pci-ps.c` probes PCI device `0x15E2`, rejects unsupported revisions, maps MMIO, allocates `struct acp63_dev_data`, selects ACP63 or ACP70 ops using the revision, and calls the inline `acp_hw_init()` wrapper.
2. Generation-specific callbacks from `ps-common.c` power on, reset, enable interrupts, read `ACP_PIN_CONFIG`, and set `is_pdm_config`/`is_sdw_config`.
3. `pci-ps.c` uses ACPI child addresses and `_WOV`/SoundWire discovery to decide whether PDM and/or SoundWire child platform devices exist, then registers `acp_ps_pdm_dma`, `dmic-codec`, `amd_ps_sdw_dma`, and an appropriate machine device.
4. PDM and SoundWire DMA drivers allocate per-stream private structures defined here during PCM open, program page tables/ring buffers in hw_params, enable interrupts, update byte counters for pointer callbacks, and call `snd_pcm_period_elapsed()` when the PCI IRQ path marks a stream interrupt.
5. PCI IRQ handling in `pci-ps.c` decodes ACP external interrupt registers, updates the interrupt-status arrays in `struct acp63_dev_data`, and invokes `acp_hw_sdw_dma_irq_thread()` for generation-specific period-elapsed handling.
6. Suspend/resume wrappers call generation-specific ops that either deinitialize ACP or preserve SoundWire wake/pad state depending on current device state.

## State and persistence behavior
`struct acp63_dev_data` is the long-lived PCI driver state and owns most cross-component state. Its lock protects shared ACP register access passed down to PDM and SoundWire DMA child data. The child platform devices store pointers back to their component data with active ALSA substreams, while per-open stream structs are allocated and attached to `runtime->private_data`.

Hardware state persists in ACP MMIO registers: power FSM state, reset status, interrupt masks/status, PDM and SoundWire DMA page tables in ACP scratch/SRAM windows, ring-buffer addresses/sizes, FIFO configuration, byte counters, wake enable/status, and pad keeper/pulldown settings. Suspend/resume code explicitly saves some pad state and preserves SoundWire wake state when needed.

## Dependencies and integration points
The header includes `<linux/soundwire/sdw_amd.h>` for AMD SoundWire manager types and `<sound/acp63_chip_offset_byte.h>` for byte-offset register constants. It depends on common Linux kernel types and APIs used by includers: `struct pci_dev`, `struct device`, `struct platform_device`, `struct resource`, `struct mutex`, `struct snd_pcm_substream`, `dma_addr_t`, `void __iomem`, `BIT()`, and errno constants.

Major integration points:

- `ps/pci-ps.c` owns PCI probe/remove/IRQ/PM orchestration and child platform registration.
- `ps/ps-common.c` defines ACP63 and ACP70 hardware callbacks and fills `struct acp_hw_ops`.
- `ps/ps-pdm-dma.c` uses PDM buffer limits, PTE offsets, interrupt masks, and PDM stream/device data structures.
- `ps/ps-sdw-dma.c` uses SoundWire stream enums, IRQ masks, ring-buffer layout, stream/device structs, and generation-specific max-stream constants.
- `ps/ps-mach.c` uses the PDM platform naming contract to register a DMIC-only ASoC card.
- `mach-config.h`/`acp-config.c` provide `snd_amd_acp_find_config()`, which affects whether the PS PCI driver binds.

## Risks and edge cases
Revision-specific branching is central. Using ACP63 stream counts or interrupt mappings on ACP70/ACP71/ACP72 can route period interrupts to the wrong substream or miss them entirely. The `ACP_HW_OPS(acp_data, cb)` macro assumes `hw_ops` and callback members are valid; the inline wrappers guard that, so direct macro use should remain limited.

The shared `acp63_base` name is historical and covers ACP70+ too, which can obscure generation-specific offset differences. PDM and SoundWire DMA page-table offsets, memory windows, and ring-buffer spacing are hard-coded hardware contracts; overlapping windows would corrupt DMA. IRQ masks are write/clear sensitive and protected only where code takes `acp_lock`; missing locking around shared interrupt-control registers can lose bits when PDM and SoundWire paths update masks concurrently.

The inline suspend/runtime-resume wrappers return `-EOPNOTSUPP` if callbacks are absent. PM code should treat that as a real unsupported operation, not as success. Documentation comments also contain minor typos and stale names, so field names in code should be trusted over prose.

## Test signals
High-value validation includes:

- Build coverage for `CONFIG_SND_SOC_AMD_PS`, `CONFIG_SND_SOC_AMD_PS_MACH`, and SoundWire-enabled/disabled configurations.
- PCI probe on ACP6.3, ACP7.0, ACP7.1, and ACP7.2 revisions, confirming the correct hardware ops are selected.
- PDM capture tests at 48 kHz/S32_LE with fixed period and buffer limits, checking DMA start/stop, pointer movement, and period interrupts.
- SoundWire playback/capture tests across both managers and all supported stream IDs, checking stream-to-IRQ mapping and period elapsed callbacks.
- Suspend/resume and runtime PM tests with active and idle PDM/SoundWire streams, including ACP70 host-wake/PME paths and pad-state restoration.
- Fault-injection or register-debug tests for ACP error IRQ handling and DMA timeout paths.
