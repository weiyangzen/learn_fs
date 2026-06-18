# sources/distributed-fs/ceph-client/drivers/mtd/spi-nor/sfdp.h

## Purpose

`sfdp.h` defines the JEDEC SFDP constants and packed structures shared by the SFDP parser and manufacturer fixups. It gives symbolic names to BFPT DWORD fields, revision values, 4-byte address mode bits, quad-enable encodings, octal read fields, command-extension bits, and parameter header layout.

## Important APIs, types, and functions

The header provides `SFDP_DWORD()` for converting one-based SFDP DWORD numbering to C array indexes and `SFDP_MASK_CHECK()` for checking multi-bit capability sets. `struct sfdp_bfpt` holds up to 20 BFPT DWORDs. `struct sfdp_parameter_header` represents an SFDP parameter header including table ID bytes, revision, length, and 24-bit table pointer.

Macro groups cover BFPT DWORD 1 address/read capability bits, DWORD 5 2-2-2/4-4-4 read support, DWORD 11 page size, DWORD 15 QER values, DWORD 16 4-byte address mode and soft reset, DWORD 17 octal STR read settings, and DWORD 18 8D command extension and byte-order flags.

## Control flow

The header has no runtime control flow, but its constants drive switch statements and field extraction in `sfdp.c` and targeted manufacturer fixups such as GigaDevice, ISSI, and Macronix post-BFPT hooks.

## State and persistence behavior

No state is stored here. The constants describe persistent capabilities encoded by flash-resident SFDP tables. The parser turns those values into mutable runtime driver state.

## Dependencies and integration points

It depends on Linux bit macros and is included by `core.h`, making these definitions available throughout the SPI NOR internals. Manufacturer files use BFPT macros to interpret data passed into post-BFPT hooks.

## Risks

A wrong mask or shift changes global SFDP interpretation. Because SFDP documentation numbers DWORDs from 1 while arrays start at 0, `SFDP_DWORD()` must be used consistently. New JESD216 revisions may add fields not represented here; unsupported values, such as 16-bit opcodes, must remain safely rejected or ignored by the parser.

## Test signals

Parser tests should cover each defined QER value, address-byte encoding, 4-byte mode encoding, octal read fields, command extension values, and manufacturer fixups that inspect BFPT DWORDs through these macros.
