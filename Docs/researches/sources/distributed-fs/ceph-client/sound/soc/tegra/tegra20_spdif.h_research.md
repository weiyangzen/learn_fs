# sources/distributed-fs/ceph-client/sound/soc/tegra/tegra20_spdif.h

## Purpose
This header defines the Tegra20 SPDIF controller's register offsets, bit fields, FIFO/status/data formats, channel/user data registers, and private driver state.

## Important APIs, types, and functions
Offsets cover control/status/strobe/FIFO CSR, data in/out, channel status RX/TX pages, and user status/data FIFOs. Macros describe TX/RX enables, channel/user transmit enables, interrupt/query bits, loopback, packing, 16/20/24/raw bit modes, sticky status bits, strobe settings, RX/TX user/data FIFO clear/attention/count fields, and several layouts for `DATA_OUT`/`DATA_IN`. `struct tegra20_spdif` stores clock, playback/capture DMA descriptors, regmap, and reset.

## Control flow
There is no executable flow. The `.c` file uses a subset of these definitions for playback-only packed 16-bit TX setup, FIFO threshold programming, trigger control, DMA address calculation, and regmap access policy.

## State and persistence
The state struct persists hardware resources and DMA configuration. Register persistence is provided by the implementation's regcache over runtime PM reset/clock cycles.

## Dependencies and integration points
The header includes `tegra_pcm.h` and is private to the Tegra20 SPDIF implementation. It contains more complete RX/channel/user definitions than the current driver actively uses, supporting future expansion or register debugging.

## Risks and edge cases
Two macros reference `SPDIF_DATA_FIFO_CSR_TU_EMPTY_COUNT_SHIFT` and `SPDIF_DATA_FIFO_CSR_TX_EMPTY_COUNT_SHIFT` without the `TEGRA20_` prefix, which would fail if those masks were compiled in active code. Current `.c` usage does not reference those masks. The broad register model includes RX support that is not surfaced by the driver.

## Test signals
Build coverage should catch any newly used typo macros. Register-level tests should verify packed 16-bit data layout, FIFO attention fields, sticky status clearing, and channel/user register offsets against hardware documentation.
