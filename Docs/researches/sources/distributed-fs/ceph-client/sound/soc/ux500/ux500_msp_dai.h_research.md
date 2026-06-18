# sources/distributed-fs/ceph-client/sound/soc/ux500/ux500_msp_dai.h

## Purpose
Private DAI-level definitions for the Ux500 MSP ASoC driver. It defines supported rates/formats, frame-period constants, channel bounds, clock IDs, and the DAI driver-private state.

## Important APIs, Types, and Functions
Important constants are `UX500_I2S_RATES`, `UX500_I2S_FORMATS`, `FRAME_PER_*`, `UX500_MSP_MIN_CHANNELS`, `UX500_MSP_MAX_CHANNELS`, and `UX500_MSP_MASTER_CLOCK`. `struct ux500_msp_i2s_drvdata` stores low-level MSP pointer, regulator, DAI format, TDM masks/slots/slot width, master clock, clocks, and OPP constraint state. It also declares `ux500_msp_dai_set_data_delay()`.

## Control Flow, State, and Persistence
No runtime flow is implemented here. The struct fields persist from platform probe through stream setup and are mutated by DAI callbacks: format, slot masks, slot count/width, master clock, and OPP constraint status.

## Dependencies and Integration Points
Includes Linux types/spinlocks and `ux500_msp_i2s.h`. It is shared by MOP500 board code and the MSP DAI implementation.

## Risks and Test Signals
Risks include declarations without implementation (`ux500_msp_dai_set_data_delay()` is not defined in the researched file set), S16-only advertised formats despite some machine code accepting S32, and fixed frame-period constants needing hardware validation. Test signals are compile/link checks, hw_params constraints, and DAI format/rate negotiation on MOP500.
