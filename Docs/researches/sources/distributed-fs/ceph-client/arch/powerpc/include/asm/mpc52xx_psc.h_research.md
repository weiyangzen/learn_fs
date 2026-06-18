# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/mpc52xx_psc.h

Purpose: defines Programmable Serial Controller register bits and layouts shared by MPC52xx/MPC512x UART, AC97, IR, I2S, SPI, and FIFO drivers.

Important APIs/types/functions: macros cover status, command, FIFO status, interrupt mask/status, input/output port bits, mode register fields, and SICR protocol bits. `struct mpc52xx_psc`, `struct mpc52xx_psc_fifo`, `struct mpc512x_psc_fifo`, and `struct mpc5125_psc` map hardware blocks. `MPC52xx_PSC_MAXNUM` depends on MPC512x support.

Control flow: drivers program mode/command/status/SICR fields for the selected protocol, then move data through typed buffer/FIFO registers and handle interrupt/FIFO status bits.

State and persistence: PSC hardware registers hold protocol, FIFO, interrupt, and port state. This header holds no software state.

Dependencies and integration points: includes PowerPC types and is consumed by serial, audio, infrared, SPI, and platform code for MPC52xx/MPC512x PSCs.

Risks: multiple SoC generations have different FIFO/register layouts; using the wrong struct corrupts register access. Comments note hardware byte-swapping behavior for CCR fields that drivers must respect.

Test signals: UART console, AC97/I2S audio, SPI/IR where available, FIFO underrun/overrun handling, interrupt mask/status tests, and builds for MPC52xx, MPC512x, and MPC5125 variants.
