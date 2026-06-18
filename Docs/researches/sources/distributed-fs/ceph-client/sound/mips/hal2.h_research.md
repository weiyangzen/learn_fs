# sources/distributed-fs/ceph-client/sound/mips/hal2.h

Purpose: Defines HAL2 hardware register constants and memory-mapped register layouts used by the SGI HAL2 ALSA driver. It covers indirect control/status registers, revision fields, DMA-port controls, Bresenham clock generators, codec control fields, AES windows, volume registers, and synth-register layout.

Important APIs/types/functions: No functions are defined. Important types are `struct hal2_ctl_regs`, `struct hal2_aes_regs`, `struct hal2_vol_regs`, and `struct hal2_syn_regs`. Important macro groups include `H2_ISR_*`, `H2_REV_*`, `H2I_DMA_PORT_EN*`, `H2I_DMA_END*`, `H2I_DAC_C*`, `H2I_ADC_C*`, `H2I_C1_*`, `H2I_C2_*`, and `H2I_BRES*`.

Control flow: `hal2.c` uses these definitions to compose indirect register addresses and bitfields for reset, detect, mixer, DMA-port enable, endian selection, DAC/ADC setup, and clock programming. The struct layouts determine offsets when casting HPC3 external register windows.

State and persistence: The header owns no state, but its bit definitions describe persistent HAL2 hardware state: reset lines, DMA enables, endian flags, attenuation/gain/mute fields, clock-generator controls, and status bits.

Dependencies/integration: Depends only on `linux/types.h` but is tightly coupled to SGI HAL2 hardware and `hal2.c`. Risks include inaccurate bit masks causing register corruption, layout padding assumptions for memory-mapped registers, and comments indicating large indirect registers while helpers only actively use 16/32-bit cases. Test signals are successful HAL2 detection, correct mixer attenuation/gain programming, proper DAC/ADC data type setup, and no register bus hangs during indirect access.
