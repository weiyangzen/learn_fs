# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smuio/smuio_10_0_2_offset.h

## Purpose
`smuio_10_0_2_offset.h` defines SMUIO 10.0.2 register offsets and base-index selectors for the AMDGPU driver. It maps symbolic `mm...` register names to numeric offsets within SMUIO address blocks so code can access scratch, pinstrap, reset, timer, TSC, and SVI telemetry registers through the normal AMD register access layer.

## Important APIs, Types, And Functions
This header exports only preprocessor constants. The public surface consists of each `mmREGISTER` offset plus a matching `mmREGISTER_BASE_IDX`. Covered blocks are `smuio_smuio_misc_SmuSmuioDec` at base address `0x5a000`, including `mmSMUIO_MCM_CONFIG`, `mmIP_DISCOVERY_VERSION`, `mmIO_SMUIO_PINSTRAP`, and `mmSCRATCH_REGISTER0` through `mmSCRATCH_REGISTER7`; `smuio_smuio_reset_SmuSmuioDec` at `0x5a300`, including `mmSMUIO_MP_RESET_INTR`, `mmSMUIO_SOC_HALT`, and `mmSMUIO_GFX_MISC_CNTL`; `smuio_smuio_ccxctrl_SmuSmuioDec`, including power-ok gap cycles and golden TSC count/increment/shadow registers; `smuio_smuio_swtimer_SmuSmuioDec`, including virtual reset request, display timers, global timer control, and power interrupt-handler control; and `smuio_smuio_svi0_SmuSmuioDec`, including plane-0 telemetry and current VID registers.

## Control Flow
There is no runtime control flow. Driver code includes the header and uses offsets with register access helpers. The expected runtime pattern is to select the correct SMUIO instance/base index, read or write the `mm...` address, and pair the raw register value with bit definitions from `smuio_10_0_2_sh_mask.h`.

## State And Persistence
The file itself stores no runtime state. It names hardware state that can be persistent for the lifetime of a boot or power-management episode: scratch registers, pinstraps, MCM/package identity, reset/SoC halt controls, golden TSC counters and shadows, virtual FLR reset requests, display timer settings, interrupt-handler credit/mask controls, and SVI telemetry/current VID. Whether a particular write persists across GPU reset, suspend, or firmware reinitialization is determined by the hardware block, not this header.

## Dependencies And Integration Points
The header depends only on inclusion by C sources and matching SMUIO 10.0.2 ASIC support. It integrates with the companion shift/mask header, AMDGPU register read/write macros, SMU reset and power-management code, display timer/interrupt code, virtualization FLR handling, IP discovery/version checks, and telemetry readers. The `BASE_IDX` values are part of the AMD register access convention and are important when a register file is split across multiple aperture/base tables.

## Risks
Incorrect offsets or base indices route reads and writes to the wrong hardware register, which can break reset, timer interrupts, firmware coordination, telemetry, or package detection. This file lacks a closing `#define` for `_smuio_10_0_2_OFFSET_HEADER`; it still uses `#ifndef`/`#endif`, but without defining the guard symbol repeated inclusion is not suppressed. That is usually harmless for identical macros if values match, but it weakens the normal include-guard contract and can produce warnings or redefinition conflicts if another include path changes a definition. Consumers must also avoid mixing these 10.0.2 offsets with masks from a different SMUIO revision.

## Test Signals
There are no direct tests. Build coverage should catch syntax and duplicate-macro problems. Runtime signals include correct IP discovery version reads, scratch register behavior, package/MCM identification, successful reset/FLR flows, display timer interrupt delivery and acknowledgement, valid golden TSC values, and reasonable SVI telemetry/VID reads on hardware that uses SMUIO 10.0.2.
