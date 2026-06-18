# sources/distributed-fs/ceph-client/sound/soc/uniphier/aio-reg.h

## Purpose
Register-map contract for the UniPhier AIO block. It defines MMIO offsets and bitfields for system glue, AIO virtual maps, PLL/control registers, input/output ports, S/PDIF framing, volume/fade, sample-rate conversion, DMA channels, and DMA ring buffers.

## Important APIs, Types, and Functions
This header exports macro APIs rather than functions. Important families include `A2*MAPCTR*` virtual mapping registers, `A2APLLCTR*` PLL control, `IPORTMX*` input port configuration, `OPORTMX*` output/SRC/S/PDIF/volume registers, `PBINMX*` and `PBOUTMX*` memory format controls, `CDA2D_*` DMA channel and ring-buffer registers, and bitfield helpers such as `SBF_()`.

## Control Flow, State, and Persistence
The file has no runtime flow, but it defines persistent hardware state touched by the common UniPhier AIO implementation. Port setup uses format, rate, clock, master/slave, mute, slot, reset, and mask fields. DMA code uses ring begin/end/read/write pointers, IRQ enable/status bits, and channel address mode fields. These registers persist in hardware until reset, suspend, or explicit helper reconfiguration.

## Dependencies and Integration Points
It depends on Linux `BIT()`/`GENMASK()` definitions and on IEC61937 constants from `aio.h`. It is included by common AIO code and underpins the SoC data in `aio-ld11.c` and `aio-pxs2.c`.

## Risks and Test Signals
Risks include incorrect bit masks for high packed fields, confusing active-low power/reset naming, macro dependence on SoC-specific map selectors, and S/PDIF repetition constants needing exact IEC61937 framing. Test signals are register-write traces during I2S/S/PDIF/SRC setup, successful reset/unmask/fade operations, IRQ status/clear correctness, and bitfield validation against UniPhier hardware manuals.
