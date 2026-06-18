# sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_asrc_common.h

## Purpose
`fsl_asrc_common.h` defines common ASRC structures and function declarations shared by the ASRC core, PCM DMA component, and compressed memory-to-memory driver. It is the cross-file contract that lets `fsl_asrc.c` provide hardware callbacks while `fsl_asrc_dma.c` and `fsl_asrc_m2m.c` implement ALSA data movement frontends.

## Important APIs, Types, and Definitions
- Direction constants `IN` and `OUT` index all two-element arrays for input/output resources.
- `enum asrc_pair_index` identifies ASRC pair contexts A through D, with this hardware using A/B/C and `PAIR_CTX_NUM` allowing four slots.
- `struct fsl_asrc_m2m_cap` reports supported compressed-M2M input/output formats, channel range, and rate arrays.
- `struct fsl_asrc_pair` stores per-conversion context: parent ASRC pointer, error flags, pair index, channel count, DMA descriptors/channels, imx DMA metadata, PCM pointer position, private extension memory, completions, M2M formats/rates/buffer lengths, DMA buffers, first-convert flag, and optional ratio modifier state.
- `struct fsl_asrc` stores shared device state: DMAengine DAI metadata, platform device, regmap, physical base, clocks, M2M ALSA card, pair table, channel availability, fixed ASRC BE rate/format, SoC flags, callback table, pair private size, and hardware-private pointer.
- Export declarations cover `fsl_asrc_component` and M2M init/exit/suspend/resume.

## Control Flow and Usage
The ASRC core initializes `struct fsl_asrc` and populates callbacks. The DMA component allocates `struct fsl_asrc_pair` instances during PCM open/new, asks the core to request/release pair slots, and uses callbacks for FIFO addresses and DMA channel selection. The M2M driver allocates pairs per compressed stream, uses the same callbacks for pair configuration/start/stop, and owns DMA-buffer export and task execution.

## State and Persistence
All structures are volatile kernel runtime state. The central stateful fields are `asrc->pair[]` and `channel_avail`, protected by the core spinlock during allocation/release, plus per-pair DMA descriptors, completions, and error flags. No state persists beyond driver lifetime except what is represented by hardware registers and regmap cache in the core.

## Dependencies and Integration Points
The header depends on ALSA DMAengine structures, compressed/M2M users, DMAengine descriptors/channels, imx DMA data, completions, regmap, clocks, and platform devices supplied by included kernel headers in the C files. It is included by all ASRC implementation files and forms the ABI between the ASRC component and the M2M driver inside the kernel tree.

## Risks and Edge Cases
- The common structures expose many fields directly, so ownership rules must be respected by all users; for example, DMA channels may be reused or released depending on `req_dma_chan`.
- `PAIR_CTX_NUM` includes D while core allocation iterates only up to `ASRC_PAIR_MAX_NUM` from `fsl_asrc.h`; cross-header changes can desynchronize capacity.
- Callback pointers are optional in places; M2M code checks some but not all callbacks before use.
- Direction indexes are plain integers, so IN/OUT inversion mistakes compile cleanly and can swap DMA/FIFO semantics.

## Test Signals
- Build all three ASRC objects together to catch signature drift.
- Run PCM DPCM and compressed M2M paths in one boot to verify common pair allocation and release remain coherent.
- Suspend/resume with M2M pairs verifies shared pair table iteration and callback expectations.
