# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/fw_lp11002.h lines 26562-29879

## Scope And Artifact

- Scope checked against `Docs/research_subset_a.md`: `sources/os/illumos/illumos-gate` is included in subset A.
- File role: embedded Emulex LP11002 firmware image header, not normal C implementation.
- This chunk is inside `static uint8_t emlxs_lp11002_image[]`.
- Firmware identity from file context: `LP11002-S: v2.82a4 (bf282a4.all)`.
- Chunk coverage: 3,318 source rows, 26,544 image bytes, firmware offsets `0x33D40` through `0x3A4EF`.

## APIs And Host Surface

- No C functions, typedefs, structs, macros, or illumos kernel APIs are declared in this line range.
- The host-visible API surface is the enclosing firmware image symbol `emlxs_lp11002_image[]`.
- `emlxs_fw.h` registers this image under `LP11002_FW` with the size, image pointer, label, and SLI/kernel/stub constants.
- `emlxs_adapters.h` maps LP11002, LP11002-S/Oracle, and LP11002 spare adapter entries to `LP11002_FW`.

## Control Flow

- Bytes follow ARM big-endian firmware-code patterns, with prologue/epilogue words, conditional branches, direct branches, and branch-with-link sequences.
- The chunk begins mid-routine at `0x33D40`; adjacent prior lines compare state at offsets around `0xB8` and `0xBC`.
- `0x33D40`-`0x341F0`: flag-test fan-out paths write global/literal-address state and call common helper/event paths.
- `0x34200`-`0x34F68`: board/global register handling and reset/DMA/error paths, with diagnostics for receive queue errors, BIUE, reset DMA, and selected-entry stalls.
- `0x34AD0`-`0x354A8`: polling/draining selected entries and related queue/list structures using offsets around `0xAC`, `0xB8`, `0x2C0`-`0x2DC`, and byte flags `0x66`/`0x67`.
- `0x35518`-`0x36970`: link/port initialization and interrupt/link accounting, including PCFG/LPCS and loop-state diagnostics.
- `0x36C50`-`0x374B8`: buffer/exchange handling for byte states `0xB0`/`0xB1`, ABTS/reject paths, and buffer fields such as `0x06`, `0x07`, `0x0C`, `0x18`, `0x58`, `0x6C`, and `0x270`.
- `0x37990`-`0x39F20`: XRI/dead-exchange checks, loop/link state-machine paths, buffer release, duplicate-get handling, and abort request lookup.
- `0x39F28`-`0x3A4EF`: begins another routine draining linked structures around `0x2C0`-`0x2DC`, `0x340`-`0x350`, and `0x78`; the chunk ends mid-routine.

## State And Data

- This chunk is firmware-private state and hardware/MMIO-style offsets, not C-visible state.
- Repeated base immediates include `0x0A...`, `0x0200...`, `0x0700...`, `0x0F00...`, `0x1900...`, and literal addresses in the `0x0008....` range.
- Frequently accessed offsets include `0x04`, `0x06`, `0x07`, `0x08`, `0x0C`, `0x18`, `0x20`, `0x24`, `0x3F`, `0x40`, `0x48`, `0x4C`, `0x58`, `0x6C`, `0x70`, `0x78`, `0x84`, `0xB8`, `0xD8`, `0x144`, `0x170`, `0x270`, `0x2C0`-`0x2DC`, `0x340`-`0x358`, `0x4F0`, and `0x700`-class offsets.
- Embedded diagnostics include `FRxQ Error %08x`, `BIUE: %08x`, `Reset DMA`, `Selected entry stuck`, `LKDN`, `LD EXP`, `ELLF`, `LDBU`, `IntL EXP`, `BARJT`, `BAACC buf`, `ABTSbuf`, `RJT buf`, `XCB 0: Can't start xchg`, `RI %x deadx %4x`, `OOOFrm`, loop initialization strings, `bad buffer rls`, `Rls free buf %x`, `dup get`, `Abt Req %x%04x`, and `Fnd abt x %x`.

## Dependencies

- Build dependency: this header only emits the actual image when `EMLXS_FW_IMAGE_DEF` is defined. Otherwise `emlxs_lp11002_image` and `emlxs_lp11002_size` are zero macros.
- Firmware table dependency: `emlxs_fw.h` includes `fw_lp11002.h` while building `EMLXS_FW_TABLE`.
- Adapter dependency: LP11002 adapter definitions in `emlxs_adapters.h` select `LP11002_FW`.
- Runtime dependency: illumos `emlxs` treats this range as opaque firmware bytes downloaded to the Emulex HBA.
- Hardware/protocol dependency: strings and offset patterns indicate assumptions about Emulex Helios/LP11002 layout, Fibre Channel link state, SLI2/SLI3 operation, DMA queues, ABTS/XRI/RPI exchange handling, and loop/port initialization.

## Risks

- Opaque binary: memory safety, concurrency, timeout behavior, and protocol correctness cannot be audited at C source level.
- Integrity risk: changing any byte, endian ordering, row count, or embedded diagnostic text changes the firmware payload.
- Boundary risk: this chunk starts and ends mid-routine, so full invariants require adjacent chunks.
- State-machine risk: incorrect firmware selection for LP11002-family adapters could cause hangs, missed interrupts, or failed Fibre Channel login/error recovery.
- Licensing/provenance: the file carries Emulex copyright/license text.

## Cross-Chunk References

- Previous chunk should explain the routine reaching line `26562`; adjacent context at lines `26552`-`26561` loads state from offsets including `0x804`, `0x638`, `0x4F0`, `0x358`, `0xB8`, and `0xBC`.
- Next chunk must continue the routine begun near `0x3A4C0`; lines after this range continue queue/list handling for fields around `0x2C8`, `0x2CC`, `0x2C0`, `0x2C4`, `0x2D8`, and `0x2DC`.
- File-level merge should preserve that this chunk is not independently callable source code; it is a middle slice of `emlxs_lp11002_image[]`, registered through `LP11002_FW` for LP11002-family adapters.