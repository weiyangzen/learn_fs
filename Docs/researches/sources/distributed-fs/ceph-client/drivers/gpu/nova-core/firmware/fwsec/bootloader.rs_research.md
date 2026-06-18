# sources/distributed-fs/ceph-client/drivers/gpu/nova-core/firmware/fwsec/bootloader.rs

## Purpose

`firmware/fwsec/bootloader.rs` wraps FWSEC in a PIO-loaded generic bootloader for Turing and GA100, where FWSEC itself cannot be loaded directly.

## Important APIs, Types, And Functions

Important types are `BootloaderDesc`, `BootloaderDmemDescV2`, and `FwsecFirmwareWithBl`. `FwsecFirmwareWithBl::new()` loads `gen_bootloader`, prepares aligned bootloader code, creates a coherent DMA mirror of FWSEC, builds the DMEM descriptor, and implements `FalconFirmware<Target = Gsp>` plus `FalconPioLoadable`. `run()` loads and executes the wrapper.

## Control Flow

`new()` parses the bootloader descriptor from a firmware binary, copies and 256-byte-aligns bootloader code, pads the FWSEC DMA image so source offsets mirror destination offsets, and fills `BootloaderDmemDescV2` with non-secure/secure code offsets, data base/size, DMA context, and entry point. It places bootloader IMEM just below the first 64 KiB. `run()` resets GSP, PIO-loads the bootloader and descriptor, configures FBIF DMA context, boots, and checks mailbox status.

## State And Persistence Behavior

The wrapper owns the coherent FWSEC DMA object, bootloader code vector, and DMEM descriptor; these must remain alive while the bootloader DMA-copies FWSEC. Hardware state persists in GSP Falcon IMEM/DMEM, FBIF transaction config, and mailbox results.

## Dependencies And Integration Points

It depends on FWSEC firmware load parameters, Falcon PIO APIs, coherent DMA, firmware request parsing, chipset firmware naming, FBIF target/mem-type enums, and GSP registers. `gsp/boot.rs` uses it when `Chipset::needs_fwsec_bootloader()` is true.

## Risks And Test Signals

Risks include assuming FWSEC has a non-secure IMEM target, requiring DMEM destination zero, offset mirroring and padding correctness, bootloader load-ceiling underflow, DMA context index validation, and coherent versus non-coherent naming mismatch. Test on Turing and GA100, malformed bootloader headers, nonzero FWSEC DMEM destinations, IMEM size near 64 KiB, mailbox failure, and WPR2 creation after wrapper execution.
