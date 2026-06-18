# sources/distributed-fs/ceph-client/sound/soc/ux500/ux500_msp_i2s.h

## Purpose
Register, bitfield, enum, and structure contract for the Ux500 MSP I2S/PCM controller. It describes the hardware register layout and the in-memory configuration consumed by `ux500_msp_i2s.c`.

## Important APIs, Types, and Functions
Defines register offsets such as `MSP_DR`, `MSP_GCR`, `MSP_TCF`, `MSP_RCF`, `MSP_SRG`, `MSP_DMACR`, interrupt/multichannel registers, bit masks for global config, protocol config, FIFO flags, DMA and interrupt bits, plus enums for protocol, phase, frame/element length, delay, edge, companding, direction, data size, state, and RX comparison mode. Important structs are `msp_multichannel_config`, `msp_protdesc`, `ux500_msp_config`, and `ux500_msp`.

## Control Flow, State, and Persistence
The header implements no flow, but `ux500_msp_config` is the transient setup object for each `open()`, while `ux500_msp` is persistent low-level state storing MMIO base, DMA data register address, MSP state, direction busy mask, loopback flag, and computed bit clock.

## Dependencies and Integration Points
Depends on Linux platform-device declarations. It is included by both the DAI layer and low-level register programming layer, and indirectly shapes MOP500 TDM behavior.

## Risks and Test Signals
Risks include dense bitfield macros where shift/mask mistakes are hard to diagnose, duplicated direction enums (`msp_direction` and `i2s_direction_t`) with different names, legacy spelling/semantic quirks, and fixed FIFO/register assumptions. Test signals are compile coverage, register dump comparison after known configurations, bitclock/frame-period validation, and TX/RX/multichannel interrupt behavior.
