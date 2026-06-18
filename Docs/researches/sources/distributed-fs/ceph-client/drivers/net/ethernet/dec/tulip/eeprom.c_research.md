# sources/distributed-fs/ceph-client/drivers/net/ethernet/dec/tulip/eeprom.c

## Purpose
Provides EEPROM/SROM support for the shared Tulip driver: reading serial EEPROM words, detecting/fixing old SROM layouts, building media tables, carrying multiport board media data forward, and optionally synthesizing media-table data for HPPA/GSC cards.

## Important APIs, Types, and Functions
Exports `tulip_parse_eeprom` and `tulip_read_eeprom`. Internal data includes `eeprom_fixups`, `block_name`, and `tulip_build_fake_mediatable`. It constructs `struct mediatable` and `struct medialeaf` instances stored in `tp->mtable`, fills flags such as `has_mii`, `has_nonmii`, `has_reset`, and may update `tp->sym_advertise`, `tp->csr12_shadow`, and CSR15 defaults.

## Control Flow and State
Parsing starts by detecting old-style EEPROMs where early bytes mirror station-address data. Missing EEPROMs can reuse the previous multiport board mediatable; known OUI/layout fixups patch substitute media-control data into EEPROM bytes. New-style tables are found through offset byte 27, then the code reads default media, optional CSR12 direction, leaf count, and each media block. Compact 21140 blocks and extended blocks are decoded differently, with special handling for reset blocks, MII blocks, Davicom delay blocks, Davicom media numbering, and custom CSR15 values. `tulip_read_eeprom` bit-bangs CSR9 with chip select, clock, command/address bits, and 16 data reads, returning swapped data for boards flagged with swapped SEEPROM.

## State and Persistence Behavior
The EEPROM is persistent board firmware data. Runtime persistence is the allocated media table under devres, cached previous mediatable/static EEPROM pointer for multiport boards, selected advertisement mask, and optional fake mediatable state for GSC hardware. The parser mutates the in-memory EEPROM copy when applying fixups but does not write EEPROM.

## Dependencies and Integration Points
Depends on `tulip.h`, PCI device devres allocation, unaligned access helpers, Tulip flags, media names, and CSR9 register semantics. The main Tulip probe path reads EEPROM bytes and calls this parser so media selection, timer, and link-change code have `tp->mtable` and advertisement state.

## Risks and Test Signals
Risks include malformed SROM lengths advancing beyond available data, static multiport state being reused incorrectly, old-board fixups matching the wrong OUI variant, Davicom block skipping changing leaf counts unexpectedly, and bit-banged EEPROM timing/address-size errors. Test signals include old-style EEPROM boards, missing EEPROM behavior, multiport cards, GSC fake media table, MII and non-MII media leaves, swapped EEPROM flag, and media selection logs matching expected table leaves.
