# sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_rpmsg.h

## Purpose

`sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_rpmsg.h` declares the private data structures shared by the RPMsg audio CPU DAI implementation. It captures per-SoC advertised rates/formats and per-device clock, low-power-audio, and buffer-size state. The source was read as a complete 47-line file.

## Important APIs, Types, and Functions

The header defines `struct fsl_rpmsg_soc_data` with `rates` and `formats`, and `struct fsl_rpmsg` with `ipg`, `mclk`, `dma`, `pll8k`, `pll11k`, `card_pdev`, `soc_data`, `mclk_streams`, `force_lpa`, `enable_lpa`, and `buffer_size[2]`. It has no functions.

## Control Flow

There is no executable flow. `fsl_rpmsg.c` populates these structures during probe, consults `soc_data` to configure the copied DAI driver, tracks stream clock ownership through `mclk_streams`, and uses buffer-size fields when integrating with the DMA/platform layer.

## State and Persistence Behavior

The header defines runtime-only platform-device state. `mclk_streams` persists while streams are configured, low-power flags persist for the device lifetime, and `buffer_size` persists as per-direction configuration. No state is file-backed.

## Dependencies and Integration Points

The header relies on Linux clock and platform-device types through the including `.c` file. Its structures are the direct contract between device-tree match data and the RPMsg DAI implementation.

## Risks and Edge Cases

The structure contains optional clock pointers, so users must handle NULL or error pointers consistently. `force_lpa` is declared but not actively used in the read implementation, which may indicate planned or out-of-tree integration. Rate fields use `int` ALSA rate masks while formats use `u64`.

## Test Signals

Compile the RPMsg driver, verify each compatible's `soc_data` is applied, check low-power buffer sizing from device tree, and run stream open/close tests that prove `mclk_streams` state is balanced.
