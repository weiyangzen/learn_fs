<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/amipcmcia.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/amipcmcia.h

## Purpose
This header provides the Amiga PCMCIA API on top of the Gayle chip. It declares card reset/configuration helpers, inline status/interrupt operations, voltage and speed constants, and Card Information Structure tuple/function IDs.

## Important APIs, Types, And Functions
- Declared functions: `pcmcia_reset()`, `pcmcia_copy_tuple()`, `pcmcia_program_voltage()`, `pcmcia_access_speed()`, `pcmcia_write_enable()`, and `pcmcia_write_disable()`.
- Inline helpers read `gayle.cardstatus`, read/ack `gayle.intreq`, and set/clear `GAYLE_IRQ_IRQ` in `gayle.inten`.
- `PCMCIA_INSERTED` tests `GAYLE_CS_CCDET`.
- Constants define valid voltages, access speeds, CIS tuple IDs, and `CISTPL_FUNCID_*` function classes.

## Control Flow
PCMCIA setup sequences reset, voltage, access speed, tuple reads, and write-enable state. Interrupt handlers read pending Gayle bits, acknowledge with `pcmcia_ack_int()`, and enable/disable IRQ delivery with the inline helpers.

## State And Persistence Behavior
Runtime state is in the Gayle registers and card CIS memory. The header owns no persistent state, but helper calls affect card power, timing, write-protect behavior, and interrupt enablement.

## Dependencies And Integration Points
It depends on `amigayle.h` for register definitions. It integrates with Amiga PCMCIA socket support and client drivers that parse CIS tuples.

## Risks And Edge Cases
`pcmcia_ack_int()` writes `0xf8` regardless of its `intreq` parameter, so callers should not expect selective acknowledgement from the argument. Incorrect voltage/speed programming can damage cards or break enumeration.

## Test Signals
Card insertion detection, CIS tuple reads, voltage and speed switching, IRQ enable/disable/ack, write-enable toggling, and network/storage PCMCIA client probing are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/amipcmcia.h -->
