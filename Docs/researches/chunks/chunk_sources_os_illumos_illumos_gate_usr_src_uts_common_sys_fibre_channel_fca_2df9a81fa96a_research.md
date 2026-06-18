# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/fw_lpe11002.h lines 6653-9970

## Scope And Artifact

- Scope: `Docs/research_subset_a.md` includes `sources/os/illumos/illumos-gate`.
- File role: generated/embedded Emulex LPe11002 firmware image header, not normal C implementation.
- This chunk is inside `static uint8_t emlxs_lpe11002_image[]`.
- Firmware identity from file context: `LPe11002-S: v2.82a4 (zf282a4.all)`.
- Chunk coverage: 3,318 contiguous source rows, representing firmware byte offsets `0x0CF18` through `0x136C7`.
- The chunk starts after setup/control flow in the previous chunk and ends mid-string/data.

## APIs And Host Surface

- No C functions, typedefs, structs, macros, or illumos kernel APIs are declared in this range.
- Host-visible surface remains only the enclosing byte array `emlxs_lpe11002_image[]`.
- The firmware header participates in the driver build only when `EMLXS_FW_IMAGE_DEF` is defined.
- Runtime consumers outside this chunk select this image through `emlxs` firmware/adapters tables for the LPe11002/Zephyr family.

## Control Flow

- Bytes decode like ARM firmware code/data, with 57 ARM-style routine prologues visible.
- The opening block around `0x0CF18`-`0x0D058` continues list/range management from the prior chunk, walking linked entries and comparing fields such as `0x08`, `0x0C`, and `0x10`.
- Routines from `0x0D1F8` through `0x0D944` traverse firmware queues rooted near context offsets `0x60`, `0x68`, `0x70`, and `0x34`.
- Blocks around `0x0D520`, `0x0DBF4`, `0x0E284`, and `0x0EEC0` copy structures and split ranges using fields `0x08` through `0x28`.
- Around `0x0F7B0`-`0x0F890`, command/status values are classified, including `0x01`, `0x02`, `0x03`, `0x11`, `0x17`, `0x1D`, `0x24`, `0x81`, `0x98`, `0x9A`, and `0x9D`.
- Around `0x0F894`-`0x0FB90`, a larger dispatcher branches to many helper routines and returns firmware error/status codes.
- Around `0x0FCF0`-`0x10290`, routines manage a hardware/object state machine with byte state at offset `0x20` and return codes including `0xD0`-`0xD9`, `0xF1`, `0xF2`, and `0xF5`.
- Later code transitions into diagnostic/self-test routines and strings near `0x12EE0`, `0x12F60`, `0x13100`, and `0x13564`.

## State And Data

- Frequently touched fields include `0x00`, `0x04`, `0x08`, `0x0C`, `0x10`, `0x14`, `0x18`, `0x1C`, `0x20`, `0x24`, `0x28`, `0x34`, `0x38`, `0x3C`, `0x40`, `0x44`, `0x60`, `0x68`, `0x70`, `0xA0`, `0xB4`, and `0x0140`.
- Repeated register/control literals include `0x00000650`, `0x0000065C`, `0x00000668`, `0x0000066C`, `0x00000670`, `0x00000678`, `0x00000734`, and `0x0000079C`.
- Embedded global/table addresses include `0x00011F74`, `0x00011F7C`, `0x00011FE0`, `0x00014C88`, and `0x00014D00`.
- Printable strings include Emulex copyright text and diagnostics: `PCI Configuration Test`, `Local Memory SRAM Test`, `On-Chip RAM Test`, `SLIM Test`, `World Wide Port Name Test`, `Timer Test`.
- Memory-test strings include `Testing with all zero bits`, `Testing with all one bits`, `Testing with mostly 5 digits`, `Testing with mostly A digits`, and `Testing with address as data`.
- Error strings include SMISR failure diagnostics, with the final `Error bit in SMISR during ad...` continuing into the next chunk.

## Dependencies

- Build dependency: byte order, row content, 8-byte alignment, and array size must be preserved exactly.
- Driver dependency: illumos `emlxs` treats this image as opaque firmware selected via surrounding firmware metadata.
- Hardware dependency: code assumes LPe11002/Zephyr HBA register layout, SLI behavior, SRAM/RAM/SLIM layout, and SMISR semantics.
- Analysis dependency: behavior is inferred from instruction shape, immediate constants, register/control offsets, and embedded strings.

## Risks

- Opaque binary: firmware safety and protocol correctness cannot be audited at C source level.
- Integrity risk: any byte edit, deletion, endian conversion, or truncated string changes executable firmware content.
- Boundary risk: chunk starts inside ongoing control flow and ends mid-string/data.
- Hardware risk: register and SMISR code can affect adapter initialization, self-test, interrupt/status handling, and link readiness.
- Provenance/licensing risk: Emulex firmware copyright and file-level license apply.

## Cross-Chunk References

- Previous chunk: line 6652 ends at offset `0x0CF10`; this chunk begins at `0x0CF18`, continuing a routine that set up registers and context pointers.
- Next chunk: line 9970 ends at `0x136C7` in the middle of an SMISR error string; chunk 4 must complete that string and continue the diagnostic routine.
- File-level merge should record chunk 3 of 23 for `fw_lpe11002.h`, firmware offsets `0x0CF18`-`0x136C7`, and avoid treating ARM-like firmware routines as host C APIs.