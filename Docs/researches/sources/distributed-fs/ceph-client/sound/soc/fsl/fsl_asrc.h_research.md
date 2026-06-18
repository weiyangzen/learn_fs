# sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_asrc.h

## Purpose
`fsl_asrc.h` is the hardware-specific ASRC register and private-data header. It defines FIFO thresholds, buffer constants, register offsets, bitfield macros, input/output clock enums, word-width encodings, configuration structures, error flags, DMA block metadata, SoC data, and private ASRC driver state consumed primarily by `fsl_asrc.c`.

## Important APIs, Types, and Definitions
- FIFO and buffer constants include `ASRC_M2M_INPUTFIFO_WML`, `ASRC_M2M_OUTPUTFIFO_WML`, `ASRC_INPUTFIFO_THRESHOLD`, `ASRC_FIFO_THRESHOLD_MIN/MAX`, `ASRC_DMA_BUFFER_SIZE`, `ASRC_MAX_BUFFER_SIZE`, and `ASRC_OUTPUT_LAST_SAMPLE`.
- Register offsets cover control, interrupt, channel-count, config, clock-source, divider, status, ratio, FIFO data, ideal-ratio, 76K/56K, machine-control, FIFO-status, and word-format registers.
- Macros such as `ASRCTR_ASRCE(i)`, `ASRCNCR_ANCi()`, `ASRCFG_PREMOD()`, `ASRCSR_AICS()`, `ASRCDRi_AICP()`, `ASRSTR_AIDU()`, `ASRMCRi_INFIFO_THRESHOLD()`, and `ASRFSTi_OUTPUT_FIFO_FILL()` encode/decode hardware fields.
- `enum asrc_inclk` and `enum asrc_outclk` expose logical clock selections for legacy and i.MX8-era clocks.
- `struct asrc_config` is the pair configuration passed into the core configurator.
- `struct fsl_asrc_soc_data` communicates SoC quirks: eDMA usage, channel-count bit width, and ASRC-before-DMA start ordering.
- `struct fsl_asrc_pair_priv` currently stores a pointer to the active configuration.
- `struct fsl_asrc_priv` stores the ASRCK clock array, SoC data, input/output clock maps, and the cached `REG_ASRCFG` value.

## Control Flow and Usage
The header itself has no control flow; it shapes the code generated in `fsl_asrc.c`. The driver builds register addresses with index macros such as `REG_ASRDI(i)`, `REG_ASRDO(i)`, `REG_ASRIDRH(i)`, and `REG_ASRMCR(i)` so pair A/B/C programming can share code. Public clock enums are translated through per-SoC `clk_map` arrays before being written to `ASRCSR`.

## State and Persistence
The persistent state represented by this header is hardware register state plus runtime private structures. `struct fsl_asrc_priv` is allocated once per platform device and keeps clock-map and regcache metadata across operations. `struct asrc_config` is a transient programming description, not a durable copy unless a caller owns its lifetime.

## Dependencies and Integration Points
It includes `fsl_asrc_common.h` for common pair and device structures. It relies on ALSA PCM format types and kernel DMA address types being available through includers. Its macros must match the ASRC reference manual and are consumed by `fsl_asrc.c` and indirectly by M2M/DMA callbacks.

## Risks and Edge Cases
- Many macros do not fully mask input values before shifting, so callers must pass already valid field-width values.
- `ASRCFG_INIRQi` and similar macros use an `i` identifier in the expansion form; incorrect usage can produce compile errors or misleading code.
- Public clock enums have sparse values up to `ASRC_CLK_MAP_LEN`; out-of-range enum values would index clock maps unsafely if validation is not added by callers.
- Buffer-size constants are shared assumptions between core and M2M; changing them requires auditing DMA buffer allocation, output-length calculations, and FIFO draining.

## Test Signals
- Compile coverage is the main test for macro shape.
- Register dumps during known-rate conversions should show expected bitfields from the macros.
- Static analysis should verify all clock enum values used by DT/bindings remain below `ASRC_CLK_MAP_LEN`.
