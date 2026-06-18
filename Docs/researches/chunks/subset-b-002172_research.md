# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_sh_mask.h lines 52182-54587

## Purpose

This chunk is a generated AMD DCN 4.1.0 register shift/mask header slice for the DRM AMD display driver. It contains no executable C logic. Its job is to publish preprocessor constants that describe bit positions and bit masks for hardware fields in display PHY transmitter blocks and HDA/Azalia audio controller blocks. Runtime driver code combines these constants with generated register offsets and AMD display register helpers to pack, update, or decode individual MMIO fields without open-coded bit arithmetic.

The range contains 2,120 `#define` lines: 1,057 `__SHIFT` macros and 1,063 `_MASK` macros. The mismatch is due to chunk boundaries. The range begins after the `RDPCSTX1_RDPCSTX_PHY_CNTL0` shift definitions, so only the final six masks for that register are in this chunk. The range ends at the comment for `AZCONTROLLER1_IMMEDIATE_COMMAND_STATUS`, with that register's field definitions continuing in the next chunk.

Although this repository is rooted under a `ceph-client` source mirror, this file belongs to AMDGPU display hardware support. It is DCN register metadata, not distributed filesystem logic.

## Important APIs, Types, And Macros

There are no functions, structs, enums, globals, allocation paths, locks, or direct register accesses in this chunk. The public interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: least-significant bit position of a hardware field.
- `<REGISTER>__<FIELD>_MASK`: already shifted mask for the same hardware field.

These names are consumed by helpers and table-generation macros such as `FD_SHIFT`, `FD_MASK`, `REG_GET`, `REG_SET`, and `REG_UPDATE`.

Major macro families in this slice are:

- `RDPCSTX1_*`: tail of the RDPCS transmitter instance 1 PHY-control layout. The visible portion covers power-gating controls, lane loopback enables, per-lane reset/disable/data-enable/request/ack fields, termination/invert/high-protection fields, per-lane rate/width/receiver-detect fields, per-lane P-state/MPLL enable fields, DPALT mode controls, PLL MPLLB clock/divider/calibration controls, fuse/readback fields, generic bus fields, scratch registers, and TX PLL update override fields.
- `RDPCSTX2_*` and `RDPCSTX3_*`: full repeated RDPCS transmitter layouts for instances 2 and 3. These include common control, clock control, interrupt/status/clear/mask fields, TX PLL update data, CR address/data windows, SRAM memory power controls, scratch/spare registers, DPALT spare controls, pattern detect controls, PHY controls 0-17, fuse fields, and TX PLL update override registers.
- `AZCONTROLLER0_*`: first HDA/Azalia controller command and response-ring register masks, including CORB/RIRB pointers, lower/upper DMA base addresses, DMA enable bits, memory-error and overrun interrupt controls, immediate-command output/input interfaces, command-status flags, DMA position-buffer base addresses, and wall-clock alias fields.
- `AZENDPOINT0_*`, `AZINPUTENDPOINT0_*`, and `AZROOT0_*`: immediate command data/index windows for endpoint, input endpoint, and root command paths.
- `AZSTREAM0_0_*` through `AZSTREAM7_0_*`: eight output stream descriptor instances. Each repeated stream has control/status bits, link position, cyclic buffer length, last valid BDL index, FIFO size, format fields, BDL lower/upper base addresses, and link-position alias fields.
- HDA global registers: `GLOBAL_CAPABILITIES`, version and payload capability fields, `GLOBAL_CONTROL`, `WAKE_ENABLE`, `STATE_CHANGE_STATUS`, `GLOBAL_STATUS`, stream payload capabilities, `INTERRUPT_CONTROL`, `INTERRUPT_STATUS`, `WALL_CLOCK_COUNTER`, and `STREAM_SYNCHRONIZATION`.
- `AZCONTROLLER1_*`: beginning of the second HDA/Azalia controller register set, through immediate command output/input fields. `AZCONTROLLER1_IMMEDIATE_COMMAND_STATUS` is only introduced by comment at the last requested line.

The RDPCSTX2 and RDPCSTX3 blocks are mechanically parallel. The AZ stream descriptor blocks are also mechanically parallel across stream instances 0 through 7.

## Control Flow

This header has no runtime control flow. Runtime behavior appears in the AMD display driver files that include the generated DCN 4.1.0 offset and shift/mask headers:

1. DCN 4.0.1 display code includes `dcn_4_1_0_sh_mask.h` together with its companion offset header.
2. Register-table or block-constructor macros expand register/field token names into numeric masks and shifts using `FD_MASK` and `FD_SHIFT`.
3. Runtime code calls register helpers such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, and `REG_UPDATE`.
4. Those helpers use this header's constants to preserve unrelated bits during read-modify-write operations, to format values before writes, and to decode status bits after reads.

The chunk therefore defines a hardware contract, not a procedure. The handwritten driver code remains responsible for all sequencing around PHY reset release, clock enablement, PLL updates, lane power transitions, DisplayPort/USB-C alternate-mode state, transmitter FIFO start, HDA ring setup, stream descriptor programming, DMA start/stop, interrupt enablement, and status polling.

## State And Persistence Behavior

The file persists no software state. It names mutable hardware state in DCN 4.1.0 MMIO registers:

- RDPCS transmitter state includes soft reset bits, SRAM reset and memory-power state, TX FIFO lane enables/start state, interrupt masks and sticky status/clear bits, per-lane PHY reset/disable/clock-ready/data-enable/request/ack handshakes, lane termination/inversion/loopback/rate/width settings, receiver-detect request/result bits, MPLL enable and P-state fields, DPALT mode/disabling/lane-count state, pattern-detect state, fuse/repair fields, and PLL update override windows.
- HDA controller state includes global reset/flush/unsolicited-response controls, controller and stream interrupt enables/status bits, wall-clock counter state, stream synchronization bits, CORB/RIRB base addresses and read/write pointers, DMA engine enables, ring sizes and capabilities, memory-error/overrun interrupt state, immediate-command busy/result-valid state, and DMA position-buffer configuration.
- HDA stream state includes stream reset/run bits, interrupt enables, FIFO and descriptor error status, FIFO-ready status, stream number and traffic-priority fields, current link position, cyclic-buffer length, BDL last-valid index, FIFO size, audio format fields, and BDL base-address fields.

Persistence semantics are hardware-defined. Some fields are latched configuration until the next modeset, audio stream reconfiguration, power transition, driver reset, or ASIC reset. Other fields are read-only status, write-one-to-clear interrupt/status bits, self-clearing request bits, sticky error flags, DMA pointers, or handshake bits. The generated masks do not encode access type, reset defaults, ordering requirements, clock-domain constraints, or side effects.

## Dependencies And Integration Points

This chunk is meaningful only when synchronized with AMD's generated DCN 4.1.0 register database and the matching offset definitions:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_offset.h` supplies the companion MMIO offsets and base indices.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn401.c` includes this header and uses `FD_MASK`/`FD_SHIFT` for DCN 4.0.1 DMUB register-table construction.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn401/irq_service_dcn401.c` includes this header for DCN 4.0.1 interrupt handling definitions.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn401/hw_factory_dcn401.c` and `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn401/hw_translate_dcn401.c` include it for DCN 4.0.1 GPIO and translation support.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn401/dcn401_clk_mgr.c` and `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn401/dcn401_resource.c` include the DCN 4.1.0 register definitions while wiring clock/resource support.

The main behavioral integration points from this exact slice are display physical-link bring-up and display audio. RDPCSTX masks affect transmitter PHY programming, lane state, PLL update flows, FIFO state, DPALT handling, and error interrupts. HDA/Azalia masks affect HDMI/DP audio controller setup, stream descriptor DMA, ring-buffer command/response handling, interrupt routing, wall-clock reads, and audio stream format programming.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong shift or mask can compile cleanly while targeting the wrong MMIO bit or clobbering an adjacent field.
- The file is generated. Manual edits risk divergence from the authoritative AMD register source, the matching offset header, firmware expectations, and silicon documentation.
- This chunk starts and ends mid-family. Whole-register conclusions for `RDPCSTX1_RDPCSTX_PHY_CNTL0` and `AZCONTROLLER1_IMMEDIATE_COMMAND_STATUS` require adjacent chunks.
- Repeated instance families are easy to corrupt in generator or copy-style updates. `RDPCSTX2` and `RDPCSTX3` should remain layout-compatible where the hardware instances are equivalent, and `AZSTREAM0_0` through `AZSTREAM7_0` should preserve identical stream descriptor layouts.
- Fields with names ending in `_MASK` can themselves have generated `_MASK_MASK` constants, such as RDPCS interrupt mask fields. Consumers must distinguish the hardware field name from the generated suffix convention.
- RDPCS reset, clock, PLL, FIFO, and lane request/ack fields are sequencing-sensitive. Incorrect masks can produce link-training failures, disabled lanes, stuck request/ack handshakes, bad DPALT transitions, FIFO underruns/errors, or displays that only fail after suspend/resume.
- PHY electrical fields such as termination, inversion, rate, width, RBOOST/IBOOST, VREG bypass, and fuse/readback controls are hardware-sensitive. Incorrect definitions may affect signal integrity or board-specific link behavior.
- HDA ring and stream DMA fields include base-address alignment masks and low unimplemented bits. Wrong masks can program malformed CORB/RIRB/BDL/DMA position addresses, leading to DMA faults, silent audio, descriptor errors, or memory-error interrupts.
- HDA interrupt and status fields include enable/status/clear-style semantics that are not visible in this header. Using a status mask as a writable configuration field, or vice versa, can drop interrupts or leave sticky error bits uncleared.

## Test Signals

Useful validation combines generator checks, build coverage, and hardware behavior:

- Build AMDGPU display support with DCN 4.0.1/DCN 4.1.0 enabled. Missing or renamed macros should fail in DMUB, IRQ, GPIO, clock-manager, resource, link, stream, or audio register-table initialization paths.
- Mechanically compare the line range against AMD's generated DCN 4.1.0 register database and the companion offset header. Account for the six `RDPCSTX1_RDPCSTX_PHY_CNTL0` masks whose shifts are before line 52182 and the `AZCONTROLLER1_IMMEDIATE_COMMAND_STATUS` fields that start after line 54587.
- Static-check that complete in-range fields have paired `__SHIFT` and `_MASK` values with compatible widths, especially repeated RDPCSTX2/RDPCSTX3 PHY controls, interrupt mask/status fields, AZ stream descriptors, BDL/CORB/RIRB address masks, and stream format fields.
- Exercise DisplayPort/USB-C alternate-mode outputs using the RDPCSTX2/RDPCSTX3 paths across cold boot, hotplug, modeset, link training, lane-count/rate changes, blank/unblank, and suspend/resume. Watch for training timeouts, stuck lane request/ack, TX FIFO errors, PLL update pending bits, and DPALT toggle interrupts.
- Exercise HDMI/DP audio with HDA controller paths across stream start/stop, sample-rate changes, multichannel formats, compressed/HBR formats, hotplug, sink changes, and suspend/resume. Watch for silent audio, CORB/RIRB errors, stream descriptor errors, FIFO errors, DMA position-buffer problems, and missing interrupts.
- Use register readback/debug traces where available to confirm that `REG_UPDATE` operations preserve adjacent fields and that status bits such as clock-on, FIFO-ready, interrupt status, CORB/RIRB pointers, stream run/reset, and immediate-command busy/result-valid move as expected.

## Cross-Chunk Notes

The previous chunk is required to see the full `RDPCSTX1_RDPCSTX_PHY_CNTL0` shift/mask pair set. The next chunk is required for the actual `AZCONTROLLER1_IMMEDIATE_COMMAND_STATUS` field definitions and the continuation of AZ controller endpoint/input/root definitions. The final merged per-file document should treat this as one slice of the broader generated DCN 4.1.0 register namespace rather than as a standalone module.
