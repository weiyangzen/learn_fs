# sources/distributed-fs/ceph-client/drivers/dma/ste_dma40.h

## Purpose
`ste_dma40.h` is the public local configuration contract for the DMA40 driver and its low-level helper code. It defines the channel mode model, DMA element and packet-size constants, maximum hardware limits, flow-control settings, and the `stedma40_chan_cfg` structure used by clients, OF translation, memcpy defaults, and LLI generation.

## Important APIs, Types, And Functions
The file exports no functions. Its important definitions are `STEDMA40_MAX_SEG_SIZE`, `STEDMA40_MAX_PHYS`, `STEDMA40_DEV_DST_MEMORY`, `STEDMA40_DEV_SRC_MEMORY`, `enum stedma40_mode`, `enum stedma40_mode_opt`, `enum stedma40_flow_ctrl`, `struct stedma40_half_channel_info`, and `struct stedma40_chan_cfg`. The half-channel info captures endianness, DMA bus width, packet size, and flow control. The full channel config adds transfer direction, high-priority/realtime flags, logical or physical mode, mode options, event/device type, source/destination half configs, and optional fixed physical-channel binding.

## Control Flow
There is no executable control flow in this header. The data defined here drives control flow in `ste_dma40.c` and `ste_dma40_ll.c`: channel filtering validates `mode`, `dir`, `dev_type`, and burst-width compatibility; allocation chooses logical or physical resources from `mode`; low-level register builders translate width, packet size, flow-control, endianness, and priority into DMA40 register fields.

## State And Persistence
The header defines the shape of in-memory configuration only. Instances of `stedma40_chan_cfg` are stored in each `d40_chan`, copied from device-tree filter data or default memcpy configs, and updated by runtime slave configuration. There is no persistent state or hardware access in this file.

## Dependencies And Integration Points
The structures use `enum dma_transfer_direction` and `enum dma_slave_buswidth` from the DMAEngine API, so this header is coupled to Linux DMAEngine types. It is included by both the main DMA40 provider and the low-level LLI builder, making it the shared semantic boundary between client-facing channel configuration and hardware-specific register encoding.

## Risks
The constants encode hardware-specific constraints that must match `ste_dma40_ll.h` register fields. A mismatch in packet-size constants between logical and physical modes would produce invalid LLIs. The `dev_type` field is overloaded for source or destination event selection depending on `dir`, which is compact but easy to misuse. The comment for `src_info` says it describes "Parameters for dst half channel" in one place, which is likely a typo and could confuse maintainers.

## Test Signals
Test coverage should verify that each supported `dma_slave_buswidth` and packet size maps correctly in low-level register output, that logical and physical memcpy defaults are accepted, that invalid mode/direction/device combinations fail in `d40_validate_conf`, and that fixed-channel and big-endian flags from OF specs survive into `d40_chan.dma_cfg`.
