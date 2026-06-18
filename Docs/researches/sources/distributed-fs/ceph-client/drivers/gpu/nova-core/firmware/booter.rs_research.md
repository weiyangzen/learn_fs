# sources/distributed-fs/ceph-client/drivers/gpu/nova-core/firmware/booter.rs

## Purpose

`firmware/booter.rs` parses, signs, and describes SEC2 Booter firmware images used to load or unload the GSP firmware during startup.

## Important APIs, Types, And Functions

Key types are `BooterFirmware`, `BooterKind`, `HsHeaderV2`, `HsFirmwareV2`, `HsSignatureParams`, `HsLoadHeaderV2`, `HsLoadHeaderV2App`, and `BooterSignature`. `BooterFirmware::new()` requests and parses `booter_load` or `booter_unload`; it implements `FalconDmaLoadable` and `FalconFirmware<Target = Sec2>`.

## Control Flow

`new()` requests the selected firmware, validates the common binary header, reads the HS header, load header, patch location, signature metadata, and app0 load descriptor, then creates a firmware object from the payload. If signatures exist, it queries the SEC2 Falcon HAL for fuse version and selects either the last signature or an indexed signature before patching it. It then derives load targets differently for Turing/GA100 versus GA102+ because the same filenames encode different layouts.

## State And Persistence Behavior

`BooterFirmware` owns a signed firmware byte vector and immutable load/BROM parameters. It persists long enough for SEC2 Falcon loading and boot. Signature patching mutates only the in-memory copy.

## Dependencies And Integration Points

It depends on firmware common parsing, SEC2 Falcon traits, chipset ordering, fuse-version HALs, bounded byte extraction, and kernel firmware loading. GSP boot uses `BooterKind::Loader` with `sec2_falcon.load()` and mailbox arguments pointing to WPR metadata.

## Risks And Test Signals

Risks include division by zero avoided through `checked_div` but nuanced empty-signature behavior, patch signature offset interpretation, chipset-based layout selection without explicit format marker, fuse-version index math, and boot address selection using source offset on GA102+. Test with signed and unsigned Booter images, malformed HS offsets, Turing/GA100 and GA102+ layouts, signature fuse variants, SEC2 boot mailbox success/failure, and missing unloader coverage.
