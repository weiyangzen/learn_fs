# sources/distributed-fs/ceph-client/sound/soc/amd/acp/amd.h

## Purpose
`amd.h` is the core private header for AMD ACP legacy drivers. It defines ACP instance IDs, memory windows, FIFO/PTE offsets, PCM limits, PDM constants, power/reset constants, common data structures, external resources, DAI ops, and helper prototypes.

## Important APIs, Types, and Functions
Important types are `struct acp_chip_info`, `struct acp_stream`, `struct acp_resource`, `struct snd_acp_hw_ops`, and `enum acp_config`. Important declarations include revision resources `rn_rsrc`, `rmb_rsrc`, `acp63_rsrc`, `acp70_rsrc`, machine tables, `asoc_acp_cpu_dai_ops`, `acp_dmic_dai_ops`, platform register/unregister helpers, machine selection, hardware init/deinit, interrupt helpers, config helpers, parameter restore helpers, DMA/PTE helpers, byte-count access, and hardware-op wrappers.

## Control Flow
There is no executable flow in the header, but it defines the contract used by PCI probe, platform drivers, PCM open/hw_params/pointer, I2S/PDM DAI callbacks, IRQ handlers, and suspend/resume restore flows.

## State and Persistence
The header defines all major volatile state containers. `acp_chip_info` is per PCI/platform device; `acp_stream` is per PCM stream; `acp_resource` is per ACP revision. Register constants describe hardware state that must be initialized and restored.

## Dependencies and Integration Points
It includes ALSA PCM/ASoC headers, `soc-acpi`, `soc-dai`, `acp_common.h`, and `chip_offset_byte.h`. It is the integration header across nearly all ACP legacy files in this subset and companion files such as I2S and legacy common code.

## Risks
This header is broad and tightly couples files through shared mutable structures. Changes to `struct acp_chip_info` or `struct acp_stream` can affect PCI, PCM, IRQ, PM, and DAI code. Register and memory-window constants must match hardware generations.

## Test Signals
Build coverage across all ACP drivers is essential. Runtime signals include correct revision-specific resource selection, stream list handling, DMA mapping, IRQ processing, and suspend/resume restoration across Renoir, Rembrandt, ACP63, and ACP70.
