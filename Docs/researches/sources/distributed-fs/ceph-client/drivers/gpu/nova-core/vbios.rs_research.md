# sources/distributed-fs/ceph-client/drivers/gpu/nova-core/vbios.rs

Purpose: extracts and parses NVIDIA VBIOS ROM images from BAR0 to locate FwSec Falcon firmware descriptors, code/data, and signatures.

Important APIs and types: `Vbios::new()` scans ROM images and builds a `FwSecBiosImage`. `VbiosIterator` reads ROM data incrementally from `ROM_OFFSET`. `BiosImage`, `PcirStruct`, `NpdeStruct`, `PciRomHeader`, `BitHeader`, `BitToken`, `PciAtBiosImage`, `FwSecBiosBuilder`, `PmuLookupTable`, and `FwSecBiosImage` model the PCI ROM, BIT table, PMU lookup table, and FwSec firmware image. Public accessors are `fwsec_image()`, `FwSecBiosImage::header()`, `ucode()`, and `sigs()`.

Control flow: the iterator reads an initial 1 KiB header window, determines image size, reads the full image, advances on 512-byte alignment, and stops on last image or scan limit. `Vbios::new()` requires a PC-AT image plus first and second FwSec images. The builder resolves Falcon data through BIT token 0x70, compensates for image contiguity assumptions, finds the production FWSEC PMU entry, then exposes descriptor, ucode bytes, and RSA signatures.

State and persistence: `Vbios` owns copied VBIOS image data in `KVec`s and no longer reads BAR0 after construction. Parsed offsets persist inside `FwSecBiosImage`.

Dependencies and integration: depends on `Bar0`, firmware descriptor/signature types, alignment helpers, `FromBytes`, and safe casts. It feeds firmware-secure boot code.

Risks: parsing is bounds-sensitive and assumes little-endian table fields. Offset compensation across PC-AT, EFI, and FwSec images is fragile. `sigs()` uses raw pointer casting after bounds checks and depends on alignment/layout of signature structures.

Test signals: no direct tests. Firmware load success, descriptor debug logging, bounds-error logs, and hardware coverage across ROM layouts are the practical validation.
