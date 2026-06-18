# sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_easrc.h

## Purpose

`sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_easrc.h` is the private hardware contract for the NXP eASRC driver. It defines the register map, bitfield encoders, FIFO and coefficient-memory constants, firmware binary record layouts, per-format metadata, per-context parameters, slot allocation state, and top-level eASRC private state consumed by `fsl_easrc.c`. The source was read as a complete 655-line file.

## Important APIs, Types, and Functions

The header is macro and type focused. Register-address helpers include `REG_EASRC_WRFIFO`, `RDFIFO`, `CC`, `CCE1`, `CCE2`, `CIA`, `DPCS0/1Rx`, `COC`, `COA`, `SFS`, ratio registers, coefficient FIFOs, IRQ registers, channel-status registers, and debug registers. Bitfield macros encode context enable/stop/watermarks, input/output format, sample positions, prefilter stage taps, access organization, datapath slot channels and memory addresses, ratio values, coefficient writes, and IRQ masks. Types include `enum easrc_word_width`, packed firmware records `asrc_firmware_hdr`, `interp_params`, `prefil_params`, `fsl_easrc_data_fmt`, `fsl_easrc_io_params`, `fsl_easrc_slot`, `fsl_easrc_ctx_priv`, and `fsl_easrc_priv`.

## Control Flow

There is no executable flow in this header. It supplies the compile-time constants used by the implementation when probe initializes regmap ranges, firmware parsing maps coefficient arrays, `hw_params` translates PCM formats into hardware fields, and runtime resume reloads coefficient memories.

## State and Persistence Behavior

The state definitions are all in-memory driver state. `fsl_easrc_ctx_priv` persists per active ASRC pair and stores normalized rates, sample formats, filter taps, coefficient pointers, initialization modes, ratio adjustments, and sample accounting. `fsl_easrc_priv` persists for the platform device and stores slot ownership, firmware pointers, firmware name, selected resampler taps, IEC958 bps values, a constant coefficient, and a firmware-loaded flag. Packed firmware structs define the expected persistent firmware image ABI but do not own storage.

## Dependencies and Integration Points

The header includes ALSA `asound.h`, i.MX DMA definitions, and `fsl_asrc_common.h`, so it is tied to the common Freescale ASRC pair model and `IN`/`OUT` direction constants. It is used directly by `fsl_easrc.c` for register programming and by any compile unit that needs eASRC-private format or firmware declarations.

## Risks and Edge Cases

Several macros are ABI-critical: any bit shift, mask, or packed layout change can break hardware programming or firmware parsing. The packed firmware structs contain large fixed coefficient arrays, so firmware producers must match the exact record shape. The source snapshot includes apparent typo hazards such as duplicate `EASRC_DPCS0R3_ST2_MA_SHIFT` and `EASRC_IRQC_OERM(v)` masking with `EASRC_IEQC_OERM_MASK`, which should be verified by build coverage.

## Test Signals

Build tests should include all eASRC users with warnings enabled. Runtime tests should indirectly cover these definitions by reading/writing all regmap ranges, loading a known-good firmware image, exercising 16/20/24/32-bit and IEC958 formats, and validating suspend/resume coefficient reload. Static checks for macro spelling, duplicate definitions, and packed struct sizes would be high-value.
