# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prm-regbits-34xx.h

## Purpose
Defines OMAP3430/3630 PRM bitfields for voltage controller/processor registers, wake group selection, reset causes, IO-chain control, power state memory banks, SmartReflex, and clock/voltage setup.

## APIs, Flow, And State
This header is declarative. It includes masks for VP config/status (`VPENABLE`, `FORCEUPDATE`, `VPx_TRANXDONE`), voltage controller I2C fields, wake group-select masks for GPIO/UART/GPT/MCBSP/DSS/IVA2, IVA reset bits, memory state masks, IO wake/chain bits, reset source shifts, and voltage control/polarity masks.

## Dependencies And Integration
Includes `prm3xxx.h` and is central to `prm3xxx.c`, OMAP3 PM init, IO wake chain reconfiguration, VP transaction completion, and reset-source translation.

## Risks And Test Signals
This file mixes OMAP3430, OMAP3630, and ES-specific fields; using the wrong revision mask can break wakeups or USB/SmartReflex behavior. Test signals are OMAP3 PM init, IO wake interrupts, SmartReflex VP transactions, reset-source reporting, and off-mode restore.
