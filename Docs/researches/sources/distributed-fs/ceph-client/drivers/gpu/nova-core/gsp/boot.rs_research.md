# sources/distributed-fs/ceph-client/drivers/gpu/nova-core/gsp/boot.rs

## Purpose

`gsp/boot.rs` orchestrates the full GSP startup sequence, from VBIOS/FWSEC/WPR2 setup through SEC2 Booter execution, GSP RISC-V activation, sequencer processing, init-done wait, and basic GPU info retrieval.

## Important APIs, Types, And Functions

Methods on `Gsp` are `run_fwsec_frts()` and `boot()`. The flow uses `Vbios`, `GspFirmware`, `FbLayout`, `FwsecFirmware`, `FwsecFirmwareWithBl`, `BooterFirmware`, `GspFwWprMeta`, command helpers `SetSystemInfo`, `SetRegistry`, `wait_gsp_init_done()`, `get_gsp_info()`, and `GspSequencer`.

## Control Flow

`boot()` loads VBIOS and GSP firmware, computes framebuffer layout, runs FWSEC-FRTS to create WPR2, parses SEC2 `booter_load`, creates WPR metadata, queues system-info and registry commands, resets and boots the GSP Falcon with LIBOS DMA address, resets and loads SEC2 Booter with WPR metadata DMA address, checks Booter mailbox, writes bootloader app version, polls for RISC-V active, runs the sequencer, waits for `GspInitDone`, then requests static GPU info.

## State And Persistence Behavior

The method consumes preallocated `Gsp` runtime state and creates temporary firmware/layout/WPR metadata objects. Persistent hardware state includes WPR2 region registers, GSP firmware in protected framebuffer memory, running GSP-RM, command queues, and Falcon OS version. Queued commands persist until GSP processes them.

## Dependencies And Integration Points

It depends on firmware files, VBIOS parsing, framebuffer HAL/layout, GSP and SEC2 Falcons, command queue, sequencer, and register polling. It is called by `Gpu::new()` during PCI probe.

## Risks And Test Signals

Risks include boot ordering sensitivity, WPR2 already existing, FWSEC scratch error handling, Booter mailbox failure, command queue use before GSP is live, RISC-V activation timeout, and temporary object lifetimes during DMA. Test cold boot, reset-required WPR2 condition, missing firmware/VBIOS failures, FWSEC and Booter error codes, sequencer execution, init-done timeout, and GPU name retrieval.
