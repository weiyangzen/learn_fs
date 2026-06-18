# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_3_0_0_sh_mask.h lines 2377-3574

## Scope

This chunk is the tail of the generated AMD DPCS 3.0.0 register shift/mask header. It covers line 2377 through the final `#endif` at line 3574, defining 1,094 preprocessor constants: 547 `__SHIFT` values and 547 matching `_MASK` values. The content is declarative only; it exposes bitfield locations for DPCS/RDPCS register programming and contains no executable functions, data structures, storage, or branching logic.

The chunk completes the `RDPCSTX3_RDPCSTX_DPALT_CONTROL_REG` field definitions started before the chunk, then defines complete repeated register-field surfaces for CR bridge instances 3 and 4, DPCSTX transmitter instances 4 and 5, and RDPCSTX transmitter/PHY instances 4 and 5.

## Purpose

The header gives AMD display driver code stable symbolic names for extracting, composing, and updating memory-mapped display PHY/control registers. Each field has a left-shift value and a 32-bit or 16-bit mask so call sites can use common register helpers to set fields without embedding raw bit positions. In this chunk, the exported constants describe DisplayPort/HDMI transmitter lanes, FIFO control, clock gating, PLL update payloads, PHY power state, lane request/ack handshakes, spread-spectrum PLL parameters, fuse-derived calibration fields, DP Alt Mode ownership controls, and DMCU-reserved views of selected DPALT PHY state.

## Exported API Surface

There are no C functions or types. The public API is a set of `#define` constants consumed by other AMDGPU display code after including this generated ASIC register header.

Important macro families:

- `DPCSSYS_CR3_DPCSSYS_CR_ADDR` / `DPCSSYS_CR3_DPCSSYS_CR_DATA` and `DPCSSYS_CR4_DPCSSYS_CR_ADDR` / `DPCSSYS_CR4_DPCSSYS_CR_DATA`: 16-bit CR address/data fields for RDPCS transmitter CR access paths.
- `DPCSTX4_DPCSTX_*` and `DPCSTX5_DPCSTX_*`: DPCS transmitter-side clock, control, CBUS, interrupt, PLL update address, and PLL update data fields.
- `RDPCSTX4_RDPCSTX_*` and `RDPCSTX5_RDPCSTX_*`: RDPCS transmitter control, clocks, interrupts, SRAM control, scratch/spare, FIFO state, DMCU DPALT blocks, PHY control registers, fuse fields, RX load values, and DPALT access-control fields.
- A carry-over `RDPCSTX3_RDPCSTX_DPALT_CONTROL_REG` group: DPALT driver-access and blocked-status fields for transmitter instance 3.

The instance 4 and instance 5 blocks are intentionally parallel. Most `RDPCSTX4_*` definitions have a same-shaped `RDPCSTX5_*` counterpart with identical shifts and masks, allowing higher-level code to choose a register instance while preserving field semantics.

## Register Areas Covered

The DPCS TX blocks (`DPCSTX4_DPCSTX_*` and `DPCSTX5_DPCSTX_*`) define:

- Symbol clock gate/enable/status bits in `DPCSTX_TX_CLOCK_CNTL`.
- PLL update request and pending bits, 10-bit/18-bit data swap/order controls, FIFO enable/start, FIFO read-start delay, and TX soft reset in `DPCSTX_TX_CNTL`.
- CBUS write delay and CBUS soft reset in `DPCSTX_CBUS_CNTL`.
- Register FIFO overflow/error clear/mask, per-lane TX FIFO errors, TX error clear, and global interrupt mask in `DPCSTX_INTERRUPT_CNTL`.
- PLL update address and 32-bit update data payload fields.

The RDPCS TX control blocks (`RDPCSTX4_RDPCSTX_*` and `RDPCSTX5_RDPCSTX_*`) define:

- CBUS, SRAM, lane FIFO, aggregate FIFO, data mode, FIFO start delay, DPALT block status, CR/non-DPALT register block enables, and TX soft reset in `RDPCSTX_CNTL`.
- External reference clock enable, per-lane TX clock enables, aggregate TX clock gate/enable/status, SRAM clock gate/enable/status, and SRAM clock bypass in `RDPCSTX_CLOCK_CNTL`.
- Register FIFO overflow, DPALT disable and four-lane toggle interrupts, per-lane FIFO errors, clear bits, and interrupt masks in `RDPCSTX_INTERRUPT_CONTROL`.
- One-bit RDPCS PLL update data, 16-bit CR address/data, SRAM memory power disable/force/state fields, full-width scratch and spare registers, and CR convert FIFO empty/full status.
- DMCU DPALT disable/block controls, including forced TX clock disable and spare bits.

The RDPCS PHY blocks define:

- Reset, test powerdown, HDMI mode, reference range, VBOOST level, RTUNE request/ack, CR mux selection, reference clock detection, SRAM init/load status, and SRAM bypass in `PHY_CNTL0`.
- Power-gating and stability bits for PCS, PMA, analog power, and DP power-gate reset in `PHY_CNTL1`.
- DP4 power-on-reset plus per-lane RX-to-TX parallel and TX-to-RX serial loopback bits in `PHY_CNTL2`.
- Per-lane DP TX reset, disable, clock ready, data enable, request, and acknowledge handshake fields in `PHY_CNTL3`.
- Per-lane termination control, inversion, EQ calculation bypass, and high-performance protection in `PHY_CNTL4`.
- Per-lane low-power detect, rate, width, DETRX request, and DETRX result in `PHY_CNTL5`.
- Per-lane power state and MPLL enable plus DPALT DP4, DPALT disable/ack, DP reference clock enable/request in `PHY_CNTL6`.
- MPLLB fractional denominator/quotient/remainder, SSC peak/step/up-spread, multiplier/dividers, MPLLB state, SSC enable, force enable, calibration force, FRACN enable, and PMIX enable across `PHY_CNTL7` through `PHY_CNTL14`.
- Fuse fields for per-lane EQ main/pre/post settings and PLL/DCO calibration (`PHY_FUSE0` through `PHY_FUSE3`), plus RX reference/VCO load values.
- DMCU-reserved DPALT mirrors of selected `PHY_CNTL3` and `PHY_CNTL6` bits, named with `_RESERVED`.
- DPALT access control (`ALLOW_DRIVER_ACCESS`, `DRIVER_ACCESS_BLOCKED`, and spare bits).

## Control Flow And State Behavior

This header has no local control flow. Runtime behavior emerges in consumer code that reads or writes hardware registers using these masks. The constants imply several state-machine surfaces that consumers must sequence correctly:

- Reset and power state transitions: soft reset, PHY reset, power-gating enables, stable status bits, and SRAM init/load done fields are expected to be toggled or polled by display bring-up and link-management code.
- Clock control: gate-disable, enable, and clock-on bits expose both requested and observed state for TX, symbol, external reference, and SRAM clocks.
- FIFO bring-up and error handling: lane FIFO enables, aggregate FIFO enable/start, read-start delay, FIFO empty/full status, overflow bits, clear bits, and interrupt masks support data-path activation and diagnostics.
- PLL programming: update request/pending plus update address/data and MPLLB fractional/SSC/divider fields support staged link-rate programming.
- PHY lane handshake: per-lane reset/disable/clock-ready/data-enable/request/ack bits encode hardware negotiation between display control logic and PHY lanes.
- DP Alt Mode ownership: driver access, blocked status, DPALT disable/toggle, DMCU-reserved fields, and register block enables model contention between the host driver, DMCU, and DPALT control paths.

No persistence is implemented in software. Hardware register values persist according to device power/reset domains. The `SCRATCH` and `SPARE` masks expose full-width register storage that may be used by firmware/driver conventions elsewhere, but this chunk does not define those conventions.

## Dependencies And Integration Points

This file depends only on C preprocessing. It is normally included alongside companion generated headers that define register addresses and possibly enum/value constants. The mask names are designed for AMD display register helper idioms such as read-modify-write macros that take a register, field mask, and shift value.

Integration points visible from the names:

- AMDGPU DRM display code under `drivers/gpu/drm/amd`, especially DC/DCE/DPCS code that configures display PHY lanes and link clocks.
- Generated ASIC register address headers for `dpcs_3_0_0`, which provide the register offsets corresponding to these field masks.
- DisplayPort, HDMI, USB-C/DP Alt Mode, and DMCU firmware coordination paths, as reflected by `DPALT`, `HDMIMODE`, `DMCU`, `MPLLB`, and per-lane DP PHY field names.
- Interrupt handling paths that inspect FIFO errors, DPALT toggles, and register FIFO overflow, then write clear bits and masks.

## Risks

- Generated-header drift is the main risk. A wrong shift or mask silently corrupts unrelated hardware bits during read-modify-write operations, especially where fields are adjacent per-lane slices.
- Instance copy/paste errors are high-impact because instance 4 and instance 5 are large parallel blocks. A single mismatched `RDPCSTX4`/`RDPCSTX5` field can route programming to the wrong register instance or use the wrong mask.
- Some fields combine command and status semantics in adjacent bits, such as request/pending, enable/clock-on, request/ack, stable status, clear bits, and interrupt masks. Consumers must not assume every defined field is writable.
- DPALT and DMCU-reserved fields imply shared ownership. Writing driver access or reserved mirror controls without checking ownership can conflict with firmware or Type-C/DP Alt Mode state.
- Full-width `SCRATCH`, `SPARE`, and PLL update data masks allow arbitrary 32-bit writes. Call sites need hardware-specific value validation before composing register data.
- The final `#endif` is in this chunk, so malformed edits here can break inclusion of the entire generated header.

## Test Signals

Useful validation signals for this chunk are mostly build-time and hardware-integration oriented:

- C preprocessing/compilation of AMDGPU display code that includes `dpcs_3_0_0_sh_mask.h`.
- Static checks that every field in the chunk has exactly one `__SHIFT` macro and one matching `_MASK` macro; this chunk currently has 547 of each.
- Generated-register consistency checks comparing this header against the source register database for DPCS 3.0.0.
- Grep or compile checks for `DPCSTX4`, `DPCSTX5`, `RDPCSTX4`, and `RDPCSTX5` consumers to catch renamed or missing macros.
- Runtime display tests on ASICs using DPCS 3.0.0: link training, hotplug, DP Alt Mode attach/detach, HDMI mode, suspend/resume, display clock changes, and interrupt/error recovery.
- Register readback during bring-up to confirm reset, clock-on, stable, FIFO, PLL pending, lane ack, DPALT blocked, and SRAM init/load status fields match expected hardware transitions.

## Chunk Notes For Merge

This chunk is self-contained for transmitter instances 4 and 5 and closes the header. Earlier chunks are expected to define address constants and the same register families for lower-numbered instances. The final merged per-file report should describe this file as a generated bitfield map rather than handwritten driver logic, and should call out the repeated per-instance pattern across all DPCS/RDPCS transmitters.
