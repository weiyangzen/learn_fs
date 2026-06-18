# sources/distributed-fs/ceph-client/drivers/gpib/agilent_82350b/agilent_82350b.h

## Purpose
`agilent_82350b.h` defines register maps, PCI identifiers, model enums, bit fields, and private state for the Agilent 82350B-family GPIB driver.

## Important APIs, Types, and Functions
The header defines vendor/device IDs for Agilent and 82350/82351 hardware, BAR index enums for 82350A and 82350B layouts, `enum board_model`, and `struct agilent_82350b_priv`. Register enums cover card mode, interrupt/event, stream status, transfer counter, TMS9914 base, and SRAM access control. Bit enums describe card mode, interrupt enable, event status, internal config, SRAM direction/FIFO enable, and 82350A BORG firmware loader status. `agilent_82350b_fifo_is_halted()` reads stream halt state.

## Control Flow and State Model
The header does not execute code beyond the inline status read. It defines how the C file maps hardware BARs and how FIFO/SRAM streaming is controlled.

## Dependencies and Integration Points
It depends on shared GPIB, PLX9050, and TMS9914 headers. Its structures are private to the Agilent driver.

## Risks and Test Signals
Register offsets and BAR indexes are hardware ABI. Mistakes here affect every transfer path. Tests should verify model detection maps correct BARs, event bits are write-cleared as expected, transfer counter complement math matches hardware, and the FIFO halt bit transitions during streaming.
