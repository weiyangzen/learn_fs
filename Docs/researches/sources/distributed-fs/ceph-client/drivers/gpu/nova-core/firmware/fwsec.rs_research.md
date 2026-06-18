# sources/distributed-fs/ceph-client/drivers/gpu/nova-core/firmware/fwsec.rs

## Purpose

`firmware/fwsec.rs` extracts FWSEC firmware from VBIOS, patches its command and signature, and runs it on the GSP Falcon to create the WPR2/FRTS protected region or perform other secure firmware tasks.

## Important APIs, Types, And Functions

Important types are `FwsecFirmware`, `FwsecCommand`, `Bcrt30Rsa3kSignature`, APPIF/DMEM mapper structs, `ReadVbios`, `FrtsRegion`, and `FrtsCmd`. `FirmwareObject<FwsecFirmware, Unsigned>::new_fwsec()` builds and patches the command payload. `FwsecFirmware::new()` selects and patches a signature, and `run()` resets, loads, boots, and checks mailbox status.

## Control Flow

`new_fwsec()` reads the FWSEC descriptor and microcode from VBIOS, finds the APPIF DMEM mapper entry, sets `init_cmd` to FRTS or SB, and writes FRTS command parameters including VBIOS read flags and framebuffer region page numbers. `FwsecFirmware::new()` then checks descriptor signatures; if present, it computes the signature index from firmware signature-version bits and hardware fuse version, fetches the matching VBIOS signature, and patches it. `run()` performs direct Falcon reset/load/boot on chipsets that do not require the bootloader wrapper.

## State And Persistence Behavior

The firmware object owns a signed in-memory FWSEC image and descriptor. Running it mutates hardware by creating WPR2, updating scratch status, and executing secure Falcon code. The firmware bytes must remain valid during load/boot only.

## Dependencies And Integration Points

It depends on VBIOS parsing, Falcon GSP support, firmware descriptor abstractions, signature patching, BAR0 IO, transmute byte views, and `FwsecFirmwareWithBl` for older chipsets. GSP boot invokes it before Booter loads the main GSP image.

## Risks And Test Signals

Risks include APPIF table parsing over packed structs, descriptor offset arithmetic, FRTS address truncation to 4 KiB page units and `u32`, signature bitmask/fuse mismatch, and direct-run use on bootloader-required chipsets. Test with VBIOS FWSEC descriptor variants, signature-count zero/nonzero cases, invalid APPIF entries, FWSEC mailbox nonzero, scratch FRTS error codes, and WPR2 register validation.
