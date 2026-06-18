# sources/distributed-fs/ceph-client/sound/pci/mixart/mixart_hwdep.c

## Purpose
This file manages miXart firmware loading and first hardware discovery. It requests and stages motherboard Xilinx, motherboard ELF, and optional AES daughterboard Xilinx firmware; synchronizes with firmware pseudo-register status values; passes the flow table address to the embedded system; initializes the mailbox; enumerates connectors and physical I/O UIDs; creates PCM/mixer devices after firmware is ready; and registers ALSA cards.

## Important APIs, types, and functions
`mixart_wait_nice_for_register_value` polls pseudo-registers with timeout and `cond_resched`. `mixart_load_elf` parses a big-endian ELF32 firmware image and copies loadable program segments into BAR0 memory. `mixart_enum_connectors` sends play and record connector enumeration messages and stores left/right connector UIDs in each card's analog/digital pipes. `mixart_enum_physio` obtains the console manager UID and physical analog I/O UIDs. `mixart_first_init` runs connector/physical enumeration and sends an initial synchronization command.

`mixart_dsp_load` is the staged firmware loader for `MIXART_MOTHERBOARD_XLX_INDEX`, `MIXART_MOTHERBOARD_ELF_INDEX`, and `MIXART_AESEBUBOARD_XLX_INDEX`. `snd_mixart_setup_firmware` requests `mixart/miXart8.xlx`, `mixart/miXart8.elf`, and `mixart/miXart8AES.xlx`, feeds them through `mixart_dsp_load`, releases each firmware object, and records `mgr->dsp_loaded` bits.

## Control flow
Firmware setup always iterates through the three firmware filenames. The motherboard Xilinx stage checks idle/already-loaded status, validates word alignment and sentinel content, writes base and size pseudo-registers, copies the image to the hard-coded BAR0 address, and marks copy finished. The ELF stage waits for Xilinx started status, resets board number and flow-table pointer, parses/copies ELF segments, marks ELF copy complete, waits for started status, and writes the host flowinfo DMA address to `MIXART_FLOWTABLE_PTR`.

The daughterboard stage waits for ELF and motherboard Xilinx readiness, waits for daughterboard presence, reads `mgr->board_type`, skips image transfer if no daughterboard exists, rejects non-AES daughterboards, coordinates size/status/base-address pseudo-registers for AES Xilinx transfer, and then waits for daughter initialization. After that, it initializes the mailbox, performs first firmware enumeration, creates PCMs for every logical card, creates the mixer once for the manager, and registers all cards.

## State and persistence behavior
Firmware progress is tracked by pseudo-register values in BAR0 and by host `mgr->dsp_loaded` bits. `mgr->board_type`, `mgr->uid_console_manager`, per-pipe connector UIDs, and per-card physical I/O UIDs are discovered after ELF startup and persist for the manager lifetime. The flow table pointer given to firmware points at a host DMA allocation created by `mixart.c`.

## Dependencies and integration points
This file depends on the Linux firmware loader, BAR memory access macros and pseudo-register offsets from `mixart_hwdep.h`, mailbox send APIs from `mixart_core.c`, message structures from `mixart_core.h`, PCM creation from `mixart.c`, and mixer creation from `mixart_mixer.c`. Firmware names are also declared through `MODULE_FIRMWARE`.

## Risks and edge cases
Firmware loading is order-sensitive and timeout-sensitive. Missing any firmware file fails setup, even when no AES daughterboard is present because the loop still requests the AES image before `mixart_dsp_load` can skip transfer. ELF parsing trusts firmware headers enough to copy program segments to BAR0 offsets; invalid firmware can fail or corrupt device memory. Pseudo-register status values are magic constants with limited validation. The physical I/O enumeration assumes at least two analog I/O UIDs per card and specific ordering between input and output halves.

## Test signals
High-value signals include firmware request success/failure paths, status transitions for Xilinx/ELF/daughter stages, correct detection of no daughterboard versus AES daughterboard, connector UID assignment for all cards, physical I/O UID assignment, card registration only after firmware setup, and cleanup on failures at each firmware stage. Logs such as "xilinx load error", "elf could not be started", "daughter board load error", and "miXart could not be set up" identify stage-specific failures.
