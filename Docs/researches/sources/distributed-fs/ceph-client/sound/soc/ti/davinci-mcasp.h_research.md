# sources/distributed-fs/ceph-client/sound/soc/ti/davinci-mcasp.h

## Purpose
Defines McASP register offsets, bit masks, serializer/FIFO controls, and public clock/divider IDs for `davinci-mcasp.c` and machine drivers.

## Important APIs/types/functions
Macros cover global control, TX/RX format/frame/clock/TDM/status/DMA-event registers, DIT status/user-data registers, serializer control, data buffers, AFIFO, GPIO pin bits, and mute bits. Public IDs include `MCASP_CLK_HCLK_*` and `MCASP_CLKDIV_*`.

## Control flow
No executable code. Macros expand in the driver register helpers and external DAI `set_sysclk`/`set_clkdiv` calls.

## State, dependencies, integration, risks, tests
No state is stored; definitions control hardware register state. It relies on Linux `BIT()` and platform data constants. Risks are wrong offsets for variants, macro precedence issues, public ID drift, and FIFO-base differences. Test register traces, full-duplex/DIT operation, machine-driver divider calls, and all compatibles.
