# sources/distributed-fs/ceph-client/drivers/gpu/nova-core/firmware.rs

## Purpose

`firmware.rs` provides common firmware parsing, request naming, Falcon descriptor abstractions, signature-patching state, module firmware metadata generation, and temporary ELF section extraction for Nova GSP boot assets.

## Important APIs, Types, And Functions

Important items are `FIRMWARE_VERSION`, `request_firmware()`, `FalconUCodeDescV2`, `FalconUCodeDescV3`, `FalconUCodeDesc`, `FalconUCodeDescriptor`, `FirmwareObject<F, SignedState>`, `FirmwareSignature`, `BinHdr`, `BinFirmware`, `ModInfoBuilder`, and `elf::elf64_section()`. Descriptor methods return IMEM/DMEM load targets and signature metadata.

## Control Flow

Firmware requests build paths like `nvidia/<chip>/gsp/<name>-570.144.bin`. `BinFirmware::new()` validates the common magic and exposes payload ranges. Descriptor implementations normalize V2 and V3 layouts into secure/non-secure IMEM and DMEM load targets. `FirmwareObject<Unsigned>` can patch a selected signature into a bounded offset or explicitly transition to signed without patching. `ModInfoBuilder` emits firmware file names for every supported chipset. The ELF helper walks ELF64 section headers to locate named sections.

## State And Persistence Behavior

Firmware bytes are stored in kernel vectors or coherent allocations owned by higher-level wrappers. The signed/unsigned state is encoded in Rust types and prevents loading unpatched firmware through wrapper APIs. Module firmware metadata persists in the built module.

## Dependencies And Integration Points

It depends on kernel firmware loading, CString formatting, transmute `FromBytes`, Falcon firmware traits, chipset names, and numeric conversion helpers. Submodules `booter`, `fwsec`, `gsp`, and `riscv` build on this common parsing layer.

## Risks And Test Signals

Risks include fixed firmware version, strict binary magic validation but limited semantic header validation, saturating descriptor arithmetic hiding malformed descriptors, temporary ELF parser assumptions, and signature state being module-local rather than globally enforced. Test with present/missing firmware files, malformed binary and ELF headers, V2/V3 descriptors, signature patch bounds, module firmware aliases, and firmware version upgrades.
