# sources/distributed-fs/ceph-client/sound/pci/ctxfi/cthw20k2.c

## Purpose

This file implements the EMU20K2/X-Fi hardware backend behind `struct hw`. It translates the generic ctxfi resource, mixer, DAIO, timer, DAC/ADC, transport, and power-management operations into MMIO register programming for 20k2-family Creative cards, including Titanium HD (`CTSB1270`) and Onkyo SE-300PCIE (`CTOK0010`) model differences.

## Important APIs, types, and functions

The exported constructors are `create_20k2_hw_obj()` and `destroy_20k2_hw_obj()`. The central object is `struct hw20k2`, which embeds `struct hw` and stores I2C addressing state plus `mic_source`. The static `ct20k2_preset` fills the hardware vtable: SRC control block allocators and setters, SRC manager enable/disable, SRCIMP mapper programming, AMIXER setters, DAI/DAO and DAIO manager operations, timer IRQ/tick accessors, card init/stop, ADC source selection, output/mic switches, suspend/resume, and raw MMIO helpers. Major internal control blocks include `src_rsc_ctrl_blk`, `src_mgr_ctrl_blk`, `srcimp_mgr_ctrl_blk`, `amixer_rsc_ctrl_blk`, `dai_ctrl_blk`, `dao_ctrl_blk`, and `daio_mgr_ctrl_blk`.

## Control flow

`hw_card_init()` starts PCI/MMIO/IRQ access with `hw_card_start()`, initializes PLL and auto-init, resets interrupt state, programs GPIO, enables the audio ring, initializes device virtual memory transport from `card_conf.vm_pgt_phys`, configures DAIO clocks/ports, initializes DAC and ADC codecs, then enables audio-ring input into SRC. Resource code above it follows a dirty-bit model: generic setters update cached control blocks, and commit functions write only dirty registers. SRC commit also clears zero buffers and programs parameter mixer pitch; DAIO commit walks transmitter/receiver dirty masks; I2C helpers unlock the chip, poll data-ready, then read/write external codecs.

## State and persistence behavior

Persistent driver state is in `struct hw20k2`, `struct hw`, hardware registers, cached resource control blocks, IRQ callback fields, MMIO mappings, and PCI region ownership. Dirty flags preserve intended register state until commit. `hw_output_switch_put()` persists output route in GPIO extended data; `hw_mic_source_switch_put()` persists the selected mic source in `hw20k2->mic_source` and WM8775 registers. Suspend stops hardware; resume reruns full card initialization from the supplied card configuration.

## Dependencies and integration points

It depends on `cthardware.h` contracts, `ct20k2reg.h` register offsets, Linux PCI/MMIO/IRQ/DMA APIs, and ctxfi resource managers in `ctsrc`, `ctamixer`, `ctdaio`, `cttimer`, and `ctatc`. `xfi.c` and ATC creation select this backend for 20k2 cards. The timer layer uses `set_timer_irq()`, `set_timer_tick()`, and `get_wc()`. Mixer controls call capability, output switch, mic source, ADC source, and SPDIF status functions through the ATC layer.

## Risks and test signals

Key risks are register bitfield drift, busy waits without timeouts in some polling paths, model-specific GPIO mistakes, I2C lock/unlock failures, missing cleanup after partial `hw_card_init()` failure, DMA mask fallback behavior, IRQ callback races during shutdown, and the static assumptions around 4K page-table pages. Test signals include successful probe/register/remove on each supported subsystem, playback/capture at 44.1/48/96/192 kHz as applicable, SPDIF status changes, ADC source switching, Titanium HD output/mic controls, suspend/resume restoration, IRQ delivery, and `dmesg` absence of PLL/auto-init/I2C errors.
