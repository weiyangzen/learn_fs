# sources/distributed-fs/ceph-client/drivers/media/pci/cx88/cx88-mpeg.c

## Purpose
`cx88-mpeg.c` is the PCI function #2 manager for cx2388x MPEG transport-stream hardware. It owns MPEG DMA setup, transport-stream interrupts, buffer queue helpers, power-management hooks, and a registration/arbitration layer used by `cx88-dvb` and `cx88-blackbird` subdrivers.

## Important APIs, Types, And Functions
Exported DMA helpers are `cx8802_start_dma()`, `cx8802_buf_prepare()`, `cx8802_buf_queue()`, and `cx8802_cancel_buffers()`. Driver-manager exports are `cx8802_get_driver()`, `cx8802_register_driver()`, and `cx8802_unregister_driver()`. Internal control includes `cx8802_stop_dma()`, `cx8802_restart_queue()`, `cx8802_mpeg_irq()`, `cx8802_irq()`, `cx8802_request_acquire()`, and `cx8802_request_release()`.

## Control Flow
Probe obtains a shared `cx88_core`, rejects boards without MPEG support, allocates `cx8802_dev`, initializes PCI/DMA/IRQ state, adds the device to `cx8802_devlist`, stores `core->dvbdev`, and asynchronously requests DVB/blackbird modules. Subdrivers register a `cx8802_driver`; the manager validates callbacks/access mode, clones the registration per live device, installs manager callbacks, and calls subdriver probe under `core->lock`. Starting DMA configures SRAM channel 28, writes TS packet length, programs DVB or blackbird-specific `TS_*` and pinmux registers, resets counters, enables PCI/TS interrupts, and starts the TS DMA engine. IRQ handling acknowledges PCI/TS bits, delegates shared core interrupts, wakes queued vb2 buffers on RISC1, and stops DMA on opcode/general errors.

## State, Persistence, And Dependencies
Persistent runtime state is `cx8802_dev`, `mpegq.active`, `vb2_mpegq`, packet size/count, `ts_gen_cntrl`, suspend state, `drvlist`, and `core->active_type_id`/`active_ref`/input snapshots. There is no disk persistence. Dependencies include PCI, DMA masks, videobuf2, cx88 SRAM/RISC helpers, board metadata, and optional module autoloading.

## Integration Points
DVB and blackbird modules use this file as the owner of function #2 hardware and must acquire/release access before programming shared resources. `cx88-video.c` checks `core->dvbdev->vb2_mpegq` before changing analog format. The shared `cx88_core_irq()` handles non-TS bits in the same PCI interrupt path.

## Risks
Hardware arbitration is subtle: DVB acquisition changes `core->input` to the DVB input and release restores `last_analog_input`. Incorrect active reference accounting can strand hardware in the wrong mode or allow blackbird/DVB conflicts. DMA error handling stops engines but does not fully drain buffers except cancel paths. Module autoload work must be flushed on remove. Resume contains FIXME reinitialization notes and relies on queue restart.

## Test Signals
Exercise DVB and blackbird attach/detach, concurrent access refusal, stream start/stop, buffer completion counts from `MO_TS_GPCNT`, IRQ loop guard, suspend/resume with active queues, module autoload, and board-specific TS pinmux/SOP programming for HVR/Pinnacle/DVICO boards.
