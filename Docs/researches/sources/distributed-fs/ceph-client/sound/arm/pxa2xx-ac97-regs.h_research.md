# sources/distributed-fs/ceph-client/sound/arm/pxa2xx-ac97-regs.h

## Purpose
This header defines the PXA AC97 controller register offsets and bit masks used by the PXA AC97 helper library.

## Important APIs, Types, And Functions
Offsets cover PCM/mic/modem control and status registers, global control/status, codec access, FIFO data, and primary/secondary audio/modem codec register windows. Bit masks define FIFO error/service bits, global reset/interrupt/clock/off bits, status completion/ready/interrupt bits, and modem/PCM end-of-chain bits. `GCR_CLKBPB` is conditionally available for PXA3xx.

## Control Flow
No executable flow exists. `pxa2xx-ac97-lib.c` uses these constants to perform register-space arithmetic and controller resets.

## State And Persistence
The header stores no software state. It describes persistent hardware state exposed through MMIO registers.

## Dependencies And Integration Points
It is a private integration contract for PXA AC97 code and PXA hardware. Register window constants are directly used to translate AC97 register numbers into controller MMIO addresses.

## Risks And Test Signals
Wrong offsets or bit meanings would cause AC97 bus hangs, wrong codec-space access, or missed completions. Test signals include correct primary codec reads/writes, reset readiness bits in `GSR`, and clearing of spurious PXA27x EOC status bits.
