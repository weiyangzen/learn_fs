# Chunk Research: fw_lp11002.h lines 19926-23243

## Scope

- Source: `sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/fw_lp11002.h`
- Chunk: 7
- Lines read: 19926-23243
- Firmware byte offsets covered: approximately `0x26DE0` through `0x2D588`
- Subset scope: `Docs/research_subset_a.md`, illumos OS/storage driver source tree.

This chunk is not C source logic in the normal sense. It is part of the `static uint8_t emlxs_lp11002_image[]` firmware image for Emulex LP11002-S Fibre Channel adapters. The readable structure is byte-encoded ARM firmware plus offset comments and a few embedded ASCII diagnostic strings.

## APIs and Exposed Interfaces

- No C functions, types, macros, or callable host APIs are defined in this chunk.
- The public host-facing artifact remains the firmware image array declared earlier in the file under `EMLXS_FW_IMAGE_DEF`; this chunk contributes contiguous bytes to that array.
- Visible firmware-side interfaces are inferred from repeated command/status byte stores into fixed offsets such as `0x07`, `0x08`, `0x0A`, `0x0B`, `0x0F`, `0x24`, `0x26`, `0x27`, `0x3C`, `0x40`, `0x44`, `0x64`, `0x70`, `0x78`, `0x79`, `0xA0`-`0xA8`, `0xB0`-`0xB3`, and `0xD0`-`0xE8`.
- Embedded diagnostic strings visible here include `REG_LOGIN %02x %06x`, `UNREG_LOGIN %02x`, `INIT %08x`, `INIT_LINK %02x`, `ENDEC PCFG:`, and `Our SID: %08x`.

## Control Flow

- The byte stream contains many ARM prologue/epilogue patterns such as `E9 2D ...` and `E8 BD ...`, so this range appears to contain multiple firmware subroutines.
- Dense dispatch regions appear around `0x283D0`-`0x28488`, `0x2B188`-`0x2B238`, and `0x2C858`-`0x2C888`.
- Repeated handler patterns load a context pointer, test small status fields, write command/status bytes to offset `0x07`, copy mailbox-like fields, then branch to shared completion/error/logging routines outside this chunk.
- Visible command/status byte values include `0x20`, `0x23`-`0x28`, `0x31`-`0x37`, `0x40`-`0x46`, `0x50`-`0x5A`, `0x80`-`0x8B`, `0xB4`/`0xB5`, and `0xC0`-`0xC4`.
- Strings and opcodes suggest Fibre Channel login/link initialization behavior, including register login, unregister login, link init, and port configuration/status handling.

## State and Data

- Repeated offsets imply firmware-private control blocks with packed fields:
  - `0x04`, `0x08`, `0x0A`, `0x0B`, `0x0F`: small flags, identifiers, or status bytes.
  - `0x10`-`0x2C`: command payload, counters, lengths, or accounting fields.
  - `0x30`-`0x4C`: extended state and address/size fields.
  - `0x50`-`0x6C`: derived values, limits, or link/session parameters.
  - `0x70`, `0x78`, `0x79`, `0xA0`-`0xA8`, `0xB0`-`0xB3`, and `0xD0` onward: global/adapter configuration state.
- Embedded firmware-local addresses recur, including `0x000831xx`, `0x000832xx`, `0x000835xx`, `0x00083684`, and `0x00081CCC`.
- Near the end, initialization/link setup code populates a larger configuration block across `0xD0`-`0xE8`, `0xF4`-`0xFC`, and `0x100`+ offsets.

## Dependencies

- Compile-time dependency: this chunk is emitted only when `EMLXS_FW_IMAGE_DEF` defines `emlxs_lp11002_image[]`.
- Runtime dependency: the illumos `emlxs` FCA driver consumes this image as opaque firmware for the LP11002 adapter family.
- Firmware-side branches/calls target routines outside this chunk, so exact handler boundaries require adjacent chunks.
- Hardware/protocol dependency: the encoded state machine is tied to Emulex LP11002 firmware, adapter mailbox/control-block formats, and Fibre Channel link/login behavior.

## Risks and Cross-Chunk References

- This is opaque vendor firmware; ordinary C review cannot validate memory safety or protocol correctness without disassembly and hardware documentation.
- Any byte edit can corrupt firmware execution. The byte order, offsets, and array continuity must remain exact.
- The chunk starts mid-firmware routine at `0x26DE0`, likely continuing from chunk 6.
- The chunk ends mid-routine/data sequence at `0x2D588`; chunk 8 is needed to complete the handler around `0x2D4A0` onward.
- Branch tables around `0x283D0`, `0x2B188`, and `0x2C858` should be correlated with adjacent chunks before assigning exact opcode names.