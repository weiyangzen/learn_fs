# sources/distributed-fs/ceph-client/sound/drivers/vx/vx_core.c

Purpose: supplies the common hardware/DSP transport, interrupt handling, boot/load, proc status, suspend/resume, and core object allocation for Digigram VX sound cards.

Important APIs, types, and functions: exported APIs include `snd_vx_check_reg_bit()`, `snd_vx_load_boot_image()`, `snd_vx_threaded_irq_handler()`, `snd_vx_irq_handler()`, `snd_vx_dsp_boot()`, `snd_vx_dsp_load()`, optional `snd_vx_suspend()/snd_vx_resume()`, and `snd_vx_create()`. Internal transport is built around `vx_send_irq_dsp()`, `vx_reset_chk()`, `vx_transfer_end()`, `vx_read_status()`, `vx_send_msg_nolock()`, `vx_send_msg()`, and RIH helpers.

Control flow: hardware-specific drivers allocate a `vx_core` with ops and hardware descriptors. Firmware setup later calls DSP boot/load functions. RMH message sending resets CHK, writes command words through TXH/TXM/TXL, triggers DSP IRQs, waits for ISR bits, reads status words, and returns VX encoded errors when the DSP reports `ISR_ERR`. The top-half IRQ validates chip state and board ack, then wakes the threaded handler. The threaded handler queries events, handles frequency changes, and dispatches PCM updates. Reset initializes audio source, clock mode, frequency, UER state, codec, DSP, PCMCIA IRQ validation, and IEC958 bits.

State and persistence: state lives in `struct vx_core`: chip status flags, locks, clock/audio source fields, UER bits, frequency, audio info, firmware pointers under PM, and runtime PCM/mixer arrays. No persistent storage exists, but firmware references are retained for resume when `CONFIG_PM` is enabled.

Dependencies and integration: uses hardware-specific `snd_vx_ops` for register I/O, reset, codec, DSP load, IRQ ack, and clock/source controls. Integrates with firmware loader, ALSA procfs, PCM/mixer creation, and kernel IRQ threading.

Risks: message transport depends on precise lock discipline; no-lock variants require callers already to hold `chip->lock` or be in a safe context. Several wait loops time out, but hardware state machines can still leave the chip stale or unusable. Fatal DSP events are logged but do not set stale state here. Test signals include register timeout paths, VX error decoding, firmware size multiple-of-three validation, IRQ event dispatch, proc status content, suspend/resume firmware reload order, and card allocation cleanup through devres.
