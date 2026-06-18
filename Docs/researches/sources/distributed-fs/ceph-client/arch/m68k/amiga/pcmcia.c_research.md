# sources/distributed-fs/ceph-client/arch/m68k/amiga/pcmcia.c

Purpose: low-level Amiga Gayle PCMCIA helper functions exported to card/IDE/PCMCIA users.

Important APIs are `pcmcia_reset()`, `pcmcia_copy_tuple()`, `pcmcia_program_voltage()`, `pcmcia_access_speed()`, `pcmcia_write_enable()`, and `pcmcia_write_disable()`. `pcmcia_reset()` pulses `gayle_reset` and waits roughly 10 ms. `pcmcia_copy_tuple()` walks attribute memory tuples up to 64 KiB, copying the matching tuple including header while accounting for Gayle attribute byte spacing.

State is the static `cfg_byte`, which preserves program-voltage and access-speed bits across calls, and Gayle hardware registers/attribute memory. Write-enable state is set through `gayle.cardstatus`.

Dependencies include `asm/amigayle.h`, `asm/amipcmcia.h`, jiffies timing, and module exports. Integration is conditional through the Amiga Makefile and used by PCMCIA-capable Amiga drivers.

Risks and test signals: tuple walking can trigger write-related interrupts as noted in comments; voltage selection must be correct to avoid hardware damage; busy waits depend on jiffies being live. Test with tuple reads for known cards, voltage/speed transitions, reset behavior, and interrupt behavior around `GAYLE_IRQ_WR`.
