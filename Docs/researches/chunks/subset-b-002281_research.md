# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_3_1_4_sh_mask.h lines 53596-55194

## Scope

This chunk is the final segment of the generated AMD DPCS 3.1.4 shift/mask header. It covers line 53596 through the closing `#endif` at line 55194 and defines 1,313 preprocessor constants: 655 `__SHIFT` macros and 658 `_MASK` macros. The uneven count is expected for this chunk boundary because the range starts in the middle of `RDPCSTX1_RDPCSTX_PHY_CNTL16`, where three mask definitions are present but the matching shifts were defined before line 53596.

The content is declarative only. It exports bitfield locations for memory-mapped DPCS/RDPCS, UNIPHY, CR, and panel power sequencer registers; it contains no C functions, structs, runtime storage, or branching logic.

## Purpose

The header provides symbolic field positions for AMDGPU display driver code that programs ASIC display PHY and panel-power hardware. Each register field is represented by a bit shift and mask so consumer code can compose read-modify-write operations without embedding raw bit constants. In this range, the exported constants cover:

- The tail of RDPCS transmitter instance 1 generic bus, byte-order, and PLL override fields.
- CR bridge address/data fields for RDPCS transmitter instances 1 and 2.
- RDPCSPIPE0/1 DP Alt Mode PHY disable/status bits.
- UNIPHY2, UNIPHY3, and UNIPHY4 reserved macro-control windows.
- A full RDPCSTX2 transmitter/PHY register surface, including clocking, FIFO, interrupt, SRAM, DP Alt Mode, PLL, fuse, and per-lane PHY controls.
- PWRSEQ0 and PWRSEQ1 GPIO, panel power sequencing, backlight PWM, timing divider, lock, and spare-register fields.

## Exported API Surface

There are no callable APIs or local types. The public interface is the macro set consumed by AMD display code after including this generated ASIC register header.

Important macro families:

- `RDPCSTX1_RDPCSTX_PHY_CNTL16`, `RDPCSTX1_RDPCSTX_PHY_CNTL17`, `RDPCSTX1_RDPCS_CNTL3`, and `RDPCSTX1_RDPCS_TX_PLL_UPDATE_*_OVRRD`: tail fields for transmitter instance 1 generic PHY buses, per-lane byte order changes, and PLL update override address/data.
- `DPCSSYS_CR1_DPCSSYS_CR_ADDR` / `DATA` and `DPCSSYS_CR2_DPCSSYS_CR_ADDR` / `DATA`: 16-bit CR access fields used to address and transfer RDPCS transmitter CR data.
- `RDPCSPIPE0_RDPCSPIPE_PHY_CNTL6` and `RDPCSPIPE1_RDPCSPIPE_PHY_CNTL6`: DPALT DP4 mode, disable request, and disable acknowledgement fields for pipe-level PHY control.
- `DCIO_UNIPHY{2,3,4}_UNIPHY_MACRO_CNTL_RESERVED0` through `RESERVED57`: full-width reserved control registers, each exposing a 32-bit reserved field.
- `RDPCSTX2_RDPCSTX_*` and `RDPCSTX2_RDPCS_*`: the main instance-2 RDPCS transmitter and PHY mask surface.
- `PWRSEQ0_*` and `PWRSEQ1_*`: parallel panel power sequencer and backlight PWM fields for two sequencer instances.

## Register Areas Covered

The `RDPCSTX2` control block defines transmitter reset, common-mode override, per-lane bit and byte ordering, interrupt mask, PLL update request/pending, request/ack enforcement, FIFO enables, FIFO start/delay controls, register-block gating, DPALT block status, clock enables/status, SRAM clocking, OCLACLK clocking, FIFO and DPALT interrupt status/clear/mask bits, SRAM memory power controls, full-width scratch/spare registers, CR convert FIFO status, and beacon/data-enable timing delays.

The `RDPCSTX2` PHY block defines reset and APB reset controls, test powerdown, HDMI mode, reference-range selection, RTUNE request/ack, CR muxing, reference-clock detection, SRAM init/load status, PCS/PMA/analog power-gating and stable status, lane loopback controls, per-lane DP TX reset/disable/clock-ready/data-enable/request/ack fields, termination/inversion/EQ bypass/high-performance protection, lane low-power detect/rate/width/DETRX fields, lane power states, MPLL enables, DPALT DP4/disable/ack, DP reference clock enable/request, MPLLB fractional/SSC/divider programming fields, fuse-derived EQ and PLL calibration fields, RX reference/VCO load values, generic PHY input/output bus fields, and byte-order controls.

The `RDPCSTX2` DP Alt Mode and DMCU-facing fields define `ALLOW_DRIVER_ACCESS`, `DRIVER_ACCESS_BLOCKED`, DPALT control spares, DMCU disable/block controls, forced TX clock disable, and DMCU-reserved mirrors of selected PHY lane request/ack and power-state fields. These names show the register surface is shared between normal driver control and firmware/Type-C DP Alt Mode coordination.

The `PWRSEQ0` and `PWRSEQ1` blocks are structurally identical. They define GPIO enable/control/mask/A-Y fields for `VARY_BL`, `DIGON`, and `BLON`; panel sequencer enable, target state, override, polarity, and state readback fields; power-up/power-down delay fields; reference dividers for panel sequencing and backlight PWM; PWM active count, fractional enable, period, bit count, frame-start update behavior, double-buffer lock/update/readback controls, and full-width spare registers.

## Control Flow And State Behavior

This header has no local control flow. Runtime behavior emerges when AMDGPU display code uses the masks with register read/write helpers.

The field names imply several hardware state machines and handshakes:

- RDPCS reset/bring-up: soft reset, PHY reset, SRAM reset, clock enable, clock-on status, SRAM init/load status, and power-gate stable fields must be sequenced by consumers during link initialization and resume.
- Link and lane activation: per-lane FIFO enables, aggregate FIFO start, data enable, lane request/ack, clock-ready, DETRX, lane rate/width, and byte/bit ordering fields define the programmable transmit datapath.
- PLL programming: PLL update request/pending, CR address/data, override address/data, MPLLB fractional numerator/denominator/remainder, SSC, divider, and force/calibration fields support staged link-rate configuration.
- Interrupt/error handling: FIFO overflow, DPALT toggles, per-lane FIFO errors, disabled-FIFO status, clear bits, and interrupt masks provide status and recovery points.
- DP Alt Mode ownership: pipe-level DPALT disable/ack, RDPCS DPALT block status, driver access gates, DMCU reserved mirrors, and forced clock-disable fields model coordination between the host driver, display firmware, and Type-C/DPALT control paths.
- Panel sequencing: PWRSEQ target state, DONE/state readback, DIGON/SYNCEN/BLON outputs, delay fields, GPIO polarity/drive controls, and PWM frame-start locking support ordered panel power and backlight transitions.

No software persistence is implemented in this file. Hardware register contents persist according to ASIC reset and power domains. The `SCRATCH`, `SPARE`, `PWRSEQ_SPARE`, UNIPHY reserved, and PWM lock/update fields expose storage or latch semantics, but this chunk does not define any higher-level policy for their contents.

## Dependencies And Integration Points

The only syntactic dependency is the C preprocessor. The masks are intended to be included with companion generated DPCS 3.1.4 address headers and used by AMDGPU/DC register helper macros that take a register, field shift, and field mask.

Integration points visible from the naming:

- AMDGPU DRM display code under `drivers/gpu/drm/amd`, especially DC/DPCS link encoder, PHY, clock, and panel-power code.
- DPCS 3.1.4 generated register address headers that provide offsets for the field masks in this file.
- DisplayPort, HDMI, USB-C/DP Alt Mode, and DMCU firmware paths, reflected by `DPALT`, `DMCU`, `HDMIMODE`, `MPLLB`, and per-lane DP TX fields.
- Panel/backlight control paths that program power-sequence timings, GPIO output enables, BL PWM period/duty, and frame-start synchronized updates.
- Interrupt handlers and diagnostic paths that inspect FIFO, DPALT, register FIFO, and lane error/status fields.

## Risks

- Generated-header drift is the primary risk. An incorrect shift or mask can silently update adjacent hardware bits during read-modify-write operations.
- The chunk contains many parallel per-lane and per-instance definitions. Copy-generation mistakes in lane offsets, masks, or instance prefixes can affect only one lane or one sequencer and be hard to catch in build tests.
- Some fields are status/readback-only while adjacent fields are writable controls, such as request/pending, enable/clock-on, request/ack, stable status, interrupt status/clear/mask, and panel state/DONE bits. Consumers must preserve access semantics from the hardware spec.
- DPALT and DMCU-reserved fields indicate shared ownership. Writing them without checking access/block status can conflict with firmware or Type-C state transitions.
- Full-width reserved, scratch, spare, and PLL update-data masks allow broad writes. Consumer code needs hardware-specific value validation and should avoid treating reserved windows as general storage.
- This range closes the header with `#endif`; malformed edits here can break all users of the generated file.

## Test Signals

Useful validation signals are build-time and hardware-integration oriented:

- Compile/preprocess AMDGPU display code that includes `dpcs_3_1_4_sh_mask.h`.
- Static checks that complete register groups have matching `__SHIFT` and `_MASK` definitions; for this chunk as sliced, the expected count is 655 shifts and 658 masks because of the partial `RDPCSTX1_RDPCSTX_PHY_CNTL16` boundary.
- Generated-register consistency checks comparing this header against the DPCS 3.1.4 register database.
- Grep/compile checks for consumers of `RDPCSTX2`, `PWRSEQ0`, `PWRSEQ1`, `DCIO_UNIPHY2`, `DCIO_UNIPHY3`, and `DCIO_UNIPHY4` macros to catch missing or renamed fields.
- Runtime display tests on ASICs using DPCS 3.1.4: DP and HDMI link training, hotplug, USB-C DP Alt Mode attach/detach, suspend/resume, panel power on/off, backlight PWM changes, and interrupt/error recovery.
- Register readback during bring-up to confirm reset, clock-on, FIFO, PLL pending, lane ack, DPALT blocked/ack, power-gate stable, panel DONE/state, and PWM update-pending transitions.

## Chunk Notes For Merge

This chunk is source-tree aligned and intentionally documents only lines 53596-55194 of `dpcs_3_1_4_sh_mask.h`. Earlier chunks should cover the beginning of `RDPCSTX1_RDPCSTX_PHY_CNTL16` and lower-numbered register blocks. The later per-file merge should describe the whole file as a generated ASIC register bitfield map, not handwritten driver logic, and should preserve the repeated instance pattern across RDPCSTX, UNIPHY, RDPCSPIPE, CR, and PWRSEQ blocks.
