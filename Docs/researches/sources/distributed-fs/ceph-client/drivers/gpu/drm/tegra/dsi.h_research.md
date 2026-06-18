# sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/dsi.h

## Purpose
`dsi.h` defines the Tegra DSI controller register offsets, bitfields, timeout/tally helpers, pad/ganged-mode fields, and hardware pixel-format enum used by `dsi.c`.

## Important APIs, Types, and Definitions
The header has no functions. It defines DSI syncpoint/context/FIFO/power/interrupt/control/status registers; host control bits for FIFO/CRC resets, transmit trigger source, raw/HS/FIFO/BTA/CRC/ECC behavior; DSI control fields for HS clock, virtual channel, format, lanes, source, video, host, and DCS mode; packet sequence and packet length registers; PHY timing and BTA timing fields through `DSI_TIMING_FIELD()`; timeout/tally fields; pad pull-down/slew/pre-emphasis fields; ganged mode start/size/control registers; raw byte-count and ultra-low-power registers; and `enum tegra_dsi_format` values used in `DSI_CONTROL_FORMAT`.

## Control Flow Role
`dsi.c` uses these definitions to configure video or command packet sequencing, host-mode DSI writes/reads, D-PHY timing, timeout handling, pad calibration, power enable/disable, ganged dual-channel windows, and status polling. The `DSI_TIMING_FIELD()` macro converts timing values and byte-clock period into packed hardware fields.

## State and Persistence
The header describes volatile DSI hardware state. Power, trigger, FIFO, packet sequence, timing, pad, timeout, and ganged-mode settings persist in controller registers until reset or reprogrammed.

## Dependencies and Integration Points
It is consumed by the Tegra DSI host/encoder implementation and indirectly connects MIPI DSI protocol concepts to Tegra-specific registers. It also relies on kernel math macros such as `DIV_ROUND_CLOSEST()` being available in the including C file.

## Risks
Most definitions are low-level bit encodings; mistakes can corrupt packet sequencing, D-PHY timing, or pad drive behavior. `DSI_TIMING_FIELD()` subtracts a hardware increment and masks to 8 bits, so invalid periods or undersized timings can wrap if not validated first. Host and video enable bits share `DSI_CONTROL`, so callers must avoid leaving conflicting modes enabled.

## Test Signals
Runtime validation comes from successful DSI panel modesets, DCS command transfers, stable PHY timing on a scope or through panel behavior, no FIFO underflow/overflow status after transfers, correct ganged-mode register values for dual-channel panels, and trace/debugfs register dumps matching the intended packet sequence and timing configuration.
