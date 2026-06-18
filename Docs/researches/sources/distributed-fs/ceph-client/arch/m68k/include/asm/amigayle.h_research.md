<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/amigayle.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/amigayle.h

## Purpose
This header maps the Amiga Gayle chip used for A1200-style IDE and PCMCIA support. It defines Gayle memory windows, main registers, interrupt/status/config bits, reset access, and IDE platform data.

## Important APIs, Types, And Functions
- `GAYLE_RAM`, `GAYLE_ATTRIBUTE`, `GAYLE_IO`, `GAYLE_IO_8BITODD`, and size macros define the PCMCIA memory and I/O windows.
- `struct GAYLE` exposes `cardstatus`, `intreq`, `inten`, and `config` registers separated by 0x1000-byte gaps.
- `gayle`, `gayle_reset`, and `gayle_attribute` are volatile register/window accessors.
- `GAYLE_CS_*`, `GAYLE_IRQ_*`, and `GAYLE_CFG_*` define PCMCIA status, interrupt, voltage, and speed bits.
- `struct gayle_ide_platform_data` carries IDE base, IRQ port, and explicit ack requirement.

## Control Flow
Drivers read `gayle.cardstatus`, acknowledge or enable interrupts through `intreq`/`inten`, program voltage/speed via `config`, and use `gayle_reset` for reset sequencing. IDE setup passes `gayle_ide_platform_data` to the relevant platform driver.

## State And Persistence Behavior
Persistent state lives in Gayle hardware registers and the platform data supplied during device registration. PCMCIA card status and interrupt bits change asynchronously with card insertion/removal and device IRQs.

## Dependencies And Integration Points
The header depends on Amiga `zTwoBase` mapping from `amigahw.h` and Linux integer types. It integrates with Amiga PCMCIA, IDE, and interrupt handling.

## Risks And Edge Cases
Status bit names are reused for different card meanings, such as BVD/status-change and busy/IRQ, so callers must interpret bits by card type and context. Odd 8-bit I/O addressing is unusual and easy to mishandle.

## Test Signals
Validate A1200 IDE probing and explicit ack, PCMCIA insert/remove detection, voltage/speed programming, interrupt enable/ack paths, attribute memory reads, and reset sequencing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/amigayle.h -->
