<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/apollohw.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/apollohw.h

## Purpose
This header maps Apollo workstation hardware for the m68k port. It describes serial controller, RTC, PIC, CPU control, timer, model-specific physical addresses, and ISA-style I/O translation.

## Important APIs, Types, And Functions
- `apollo_model` and physical address globals describe selected machine layout.
- `struct SCN2681` maps a dual UART register file with alternating dummy bytes.
- `struct mc146818` maps RTC fields.
- `SAU7_*` and `SAU8_*` constants provide model-specific register offsets.
- `sio01`, `sio23`, `rtc`, `cpuctrl`, `pica`, `picb`, `apollo_timer`, and `addr_xlat_map` are direct memory-mapped accessors.
- `isaIO2mem(x)` translates ISA I/O addresses into Apollo memory space.

## Control Flow
Platform setup selects address globals based on bootinfo/model. Drivers then directly access UARTs, RTC, PICs, CPU control, and timer through volatile pointers and translated I/O addresses.

## State And Persistence Behavior
State lives in hardware registers and selected global physical address variables. RTC values persist in hardware; serial/PIC/timer control persists until reprogrammed or reset.

## Dependencies And Integration Points
The file depends on Apollo bootinfo and Linux types. It integrates with Apollo platform setup, serial, RTC, interrupt, timer, and bus I/O code.

## Risks And Edge Cases
Wrong model address selection maps drivers to invalid hardware. `DECLARE_2681_FIELD` depends on byte spacing matching the SCN2681 bus wiring. `isaIO2mem()` is bit-level address translation and should be changed only with hardware validation.

## Test Signals
Apollo boot, UART console, RTC read/write, PIC interrupt delivery, timer tick, CPU control register access, and ISA I/O translated device access validate the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/apollohw.h -->
