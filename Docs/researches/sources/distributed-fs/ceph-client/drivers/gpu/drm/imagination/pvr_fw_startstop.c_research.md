# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_fw_startstop.c

## Purpose
Sequences GPU/FW hardware start and stop: AXI ACE-Lite configuration, BIF catalogue programming, SLC setup, soft-reset sequencing, processor wrapper boot, RISC-V boot trigger, and idle polling before shutdown reset.

## Important APIs, types, and functions
- `pvr_fw_start()` performs hardware reset release and firmware processor boot.
- `pvr_fw_stop()` waits for idle, detaches MTS thread associations, performs extra BIF/SLC idle checks, handles META debugger state and MARS-layout differences, then asserts soft reset.
- Helpers `rogue_axi_ace_list_init()`, `rogue_bif_init()`, and `rogue_slc_init()` program bus, MMU catalogue, and SLC control registers.

## Control flow
Start optionally disables secure bus protection, clears RISC-V boot, asserts full soft reset, releases Rascal/Dust, releases everything except the firmware processor, initializes SLC, runs the processor-specific wrapper, configures AXI ACE-Lite, programs BIF catalogue bases for non-MIPS processors, delays for reset timing, releases the firmware processor, and for RISC-V writes `FWCORE_BOOT`.

Stop checks feature `layout_mars`, waits for Sidekick and SLC idle when applicable, clears MTS DM associations for thread 0 and additionally thread 1 on META, polls BIF and BIFPM MMU/read/SLC status registers, repeats idle checks, optionally reads META halt status to skip Garten idle when a debugger is attached, waits for Garten or MARS idle as appropriate, then asserts the platform-specific soft-reset mask.

## State and persistence
The file does not own C objects but mutates persistent hardware register state: soft reset, bus coherency, BIF/FWCORE page catalogue bases, SLC control, wrapper configuration, MTS associations, and RISC-V boot control. The state persists in hardware until reset or reprogramming.

## Dependencies and integration points
Depends on firmware processor type and callbacks, PVR feature/quirk queries, kernel VM page-table root DMA address, register read/write/poll helpers, META slave-port read helper, and common firmware init/fini. Called by `pvr_fw_init()` and unwind/fini paths.

## Risks
Start/stop is timing and platform-order sensitive. Wrong soft-reset masks, missing delays, MIPS/non-MIPS BIF differences, secure bus handling, SLC cache policy, or idle-poll masks can hang the GPU or fail boot. Stop has multiple timeout paths and META debugger behavior alters Garten idle waiting.

## Test signals
Boot and shutdown on META, MIPS, and RISC-V processors; timeout returns from SLC/Sidekick/BIF polls; RISC-V FWCORE boot transitions; secure bus feature coverage; MARS-layout cores; and suspend/resume or hard-reset loops are key signals.
