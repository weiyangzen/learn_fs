<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/adv748x/adv748x-core.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/adv748x/adv748x-core.c

## Purpose
`adv748x-core.c` is the parent I2C driver for the ADV748x HDMI/analog receiver family. It creates page-specific ancillary I2C clients and regmaps, parses OF graph endpoints, resets and initializes hardware, owns global state and media link setup, powers CSI transmitters, and instantiates HDMI, AFE, TXA, and TXB subdevices.

## Important APIs, Types, and Functions
- `struct adv748x_state` in `adv748x.h` is the shared parent state.
- Register helpers `adv748x_read()`, `adv748x_write()`, and `adv748x_write_block()` wrap regmap access for each device page.
- `adv748x_initialise_clients()` and `adv748x_set_slave_addresses()` create and program ancillary page addresses.
- `adv748x_reset()` performs software reset, slave address setup, HDMI/AFE register scripts, default input, TX reset pulse, IO datapath enables, virtual channel setup, and CP freerun configuration.
- `adv748x_tx_power()` sequences TXA/TXB MIPI D-PHY/CSI power-up/down.
- `adv748x_link_setup()` updates internal HDMI/AFE-to-TX routing and IO register 0x10 lane/source bits.
- `adv748x_parse_dt()` records one endpoint per port and validates CSI-2 lane counts.

## Control Flow
Probe allocates parent state, initializes mutex and TX identity fields, parses device-tree endpoints, configures IO regmap, reads chip revision, creates all non-IO page clients/regmaps, resets hardware, initializes HDMI and AFE subdevices, then initializes TXA and TXB subdevices. TX registered callbacks later register internal HDMI/AFE subdevices and create media links. Remove cleans up subdevices, clients, endpoint node references, and mutex. Resume calls `adv748x_reset()` early to restore hardware registers.

## State and Persistence
Endpoint node references, I2C client pointers, regmaps, child subdevice state, active TX source pointers, lane counts, and mutex are held in memory. Hardware register state is reconstructed by reset/resume. Media link state affects `state->afe.tx`, `state->hdmi.tx`, and each `tx->src`; these values drive streaming power decisions.

## Dependencies and Integration Points
The core depends on I2C ancillary device support, regmap, OF graph, V4L2 fwnode endpoint parsing, V4L2 subdev/media APIs, and child modules. Device tree must expose at least one input endpoint and one output endpoint, and TXA/TXB lane counts must follow hardware constraints.

## Risks
- `adv748x_subdev_init()` uses `is_tx(adv748x_sd_to_csi2(sd))` for all subdevices; this relies on structure layout assumptions and is risky for non-TX subdevices.
- Some reset-time writes ignore return values after helper calls, so partial initialization may be missed.
- Link setup forbids multiple sources per TX but does not perform full topology validation beyond media link constraints.
- TX power contains undocumented required writes and a `WARN_ONCE` for an unknown bit; regressions are hardware/firmware sensitive.
- Endpoint parsing stores node refs before lane parse completion, so error cleanup must run to avoid leaks.

## Test Signals
Test OF graphs for ADV7481/ADV7482 variants, invalid duplicate endpoints, missing input/output endpoints, TXA lane counts 1/2/4 and invalid values, TXB one-lane enforcement, chip revision read failure paths, reset register sequence, media link enable/disable permutations, AFE-to-TXA active-lane reduction, HDMI-to-TXA restoration, suspend/resume reset, and module unload cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/adv748x/adv748x-core.c -->
