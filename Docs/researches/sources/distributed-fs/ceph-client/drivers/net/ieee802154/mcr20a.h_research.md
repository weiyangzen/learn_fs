# sources/distributed-fs/ceph-client/drivers/net/ieee802154/mcr20a.h

## Purpose
`mcr20a.h` is the register map and bitfield definition header for the NXP MCR20A transceiver driver. It names direct access registers, indirect access registers, and bit masks used by `mcr20a.c` for radio initialization, IRQ handling, filtering, CCA, power, and packet sequencing.

## Important APIs, types, and functions
The header does not define functions or structs. Its important exported symbols are `DAR_*` register addresses, `IAR_*` indirect register addresses, IRQ status bits, `DAR_PHY_CTRL*` masks, source address matching bits, RX frame filter bits, dual PAN bits, CCA control bits, pad controls, sequence manager bits, and test/DTM/TX mode flags.

## Control flow
There is no runtime control flow. The constants are consumed by `mcr20a.c` in regmap readability/writeability policies, initialization overwrite tables, TX/RX sequence management, IRQ decoding, and mac802154 configuration callbacks.

## State and persistence
No state is stored here. The definitions are a compile-time hardware contract; incorrect values persist as misprogrammed hardware registers at runtime.

## Dependencies and integration points
The file is private to the MCR20A driver and depends only on kernel bit macros being available through the including C file. It is coupled tightly to NXP datasheet semantics and to the `mcr20a.c` regmap configs.

## Risks and test signals
Primary risks are misspelled register comments, bit definition mistakes, and stale datasheet mapping. A notable typo-like risk is `IAR_ANT_AGC_CTRL_ANTX_MASK` referencing `BIT(AR_ANT_AGC_CTRL_ANTX_SHIFT)`, where the apparent `I` prefix is missing; compile coverage should catch this if the macro is used. Test signals include allmodconfig/build coverage, register read/write smoke tests on hardware, static checks for unused or malformed bit macros, and cross-checking each writable/readable register list against this header.
