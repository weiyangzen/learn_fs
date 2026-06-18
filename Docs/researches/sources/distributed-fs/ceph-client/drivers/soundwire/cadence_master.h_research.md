# sources/distributed-fs/ceph-client/drivers/soundwire/cadence_master.h

## Purpose
Defines the shared Cadence SoundWire master data structures and exported function contract used by platform drivers. It describes PDI/stream metadata, the main `struct sdw_cdns` context, helper macros, and prototypes for initialization, IRQ, PM, port/stream, debugfs, transfer, and BPT/BRA functions.

## Important APIs, Types, and Functions
Key types are `struct sdw_cdns_pdi`, `struct sdw_cdns_streams`, `struct sdw_cdns_stream_config`, `struct sdw_cdns_dai_runtime`, and `struct sdw_cdns`. The `bus_to_cdns()` macro converts `struct sdw_bus *` to the containing Cadence context. Prototypes cover `sdw_cdns_probe()`, IRQ handlers, reset/init/PDI/clock helpers, debugfs initialization, PDI allocation/configuration, message transfer callbacks, bus config, ASoC stream setup, config update, and BPT/BRA buffer helpers.

## Control Flow
The header has no standalone execution. Platform drivers allocate and initialize `struct sdw_cdns`, call `sdw_cdns_probe()` and `sdw_cdns_init()`, install the Cadence transfer callbacks in their `sdw_bus`, and use the PDI/DAI helpers during ASoC stream setup. The stream framework calls Cadence port ops installed by `sdw_cdns_probe()`.

## State and Persistence Behavior
`struct sdw_cdns` persists for the master lifetime and owns the embedded `sdw_bus`, response buffer, completion, port/PDI data, stream runtime pointers, work items, link/interrupt flags, and status lock. `struct sdw_cdns_dai_runtime` persists per active DAI stream and is allocated/freed by `cdns_set_sdw_stream()`.

## Dependencies and Integration Points
Includes `<sound/soc.h>` and the private `bus.h`, making it a bridge between SoundWire core, Cadence hardware, and ASoC platform glue. Exported prototypes are implemented in `cadence_master.c` and consumed by Intel or other Cadence-IP platform drivers.

## Risks
The header exposes many internals of `struct sdw_cdns`; platform drivers can depend on layout details and make refactors risky. PDI arrays and DAI runtime arrays must be sized consistently by the platform glue. `ip_offset` selects between register layouts, so callers must initialize it correctly before using register helpers. BPT helpers require caller-provided DMA buffers sized from the matching calculator.

## Test Signals
Compile platform drivers against this header, probe Cadence-backed masters, verify PDI counts and DAI runtime allocation, run IRQ and PM paths, exercise both normal register transfers and BPT helpers, and check debugfs availability under `CONFIG_DEBUG_FS`.
