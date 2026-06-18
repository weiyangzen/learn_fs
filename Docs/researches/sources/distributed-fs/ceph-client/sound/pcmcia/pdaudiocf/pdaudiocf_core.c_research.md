# sources/distributed-fs/ceph-client/sound/pcmcia/pdaudiocf/pdaudiocf_core.c

## Purpose

This file is the core hardware setup and lifecycle layer for the Sound Core PDAudioCF PCMCIA capture card. It initializes the `snd_pdacf` object, exposes a proc status entry, controls FPGA reset/powerdown, bridges the AK4117 S/PDIF receiver into ALSA, and restores register state across reinitialization and power management.

## Important APIs, types, and functions

`snd_pdacf_create()` allocates and attaches `struct snd_pdacf` to the ALSA card, initializes `reg_lock` and `ak4117_lock`, and creates `/proc/asound/.../pdaudiocf`. `snd_pdacf_ak4117_create()` resets the FPGA, creates the AK4117 helper with `pdacf_ak4117_read()` and `pdacf_ak4117_write()`, programs FPGA test/control, sample format, LED, and interrupt-enable registers, and installs `snd_pdacf_ak4117_change()` as the lock/error callback. `pdacf_reinit()`, `snd_pdacf_powerdown()`, `snd_pdacf_suspend()`, and `snd_pdacf_resume()` own the restore path.

## Control flow

AK4117 register access waits for the PDAUDIOCF serial-port-busy bit, performs 16-bit port I/O through the FPGA AK interface register, and times out with device errors. Card bring-up calls `pdacf_reset()`, constructs the AK4117 instance, configures 24-bit input and interrupt/LED behavior, then updates LED status from AK4117 lock state. Suspend disables hardware interrupt sources with raw `inw/outw` so the cached register map is preserved, marks the chip suspended, powers down, and resume resets, restores SCR/TCR/IER, reinitializes AK4117, waits briefly for PLL lock, and returns ALSA power state to D0.

## State and persistence behavior

The file persists FPGA state in `chip->regmap`, AK4117 state in `chip->ak4117`, suspend SCR in `chip->suspend_reg_scr`, and status bits in `chip->chip_status`. `reg_lock` protects cached register updates; `ak4117_lock` serializes AK4117 port transactions. Direct raw writes are intentionally used during suspend/powerdown to avoid corrupting the saved register cache.

## Dependencies and integration points

It depends on `pdaudiocf.h` register helpers, ALSA core/proc/power APIs, and `sound/ak4117` receiver support. It is called by the PCMCIA front-end and by `pdaudiocf_pcm.c` close/prepare paths. IRQ and PCM code rely on `chip->ak4117`, interrupt enable bits, and the cached SCR/TCR/IER values established here.

## Risks and test signals

Risks include busy-wait timeout behavior on card removal, stale cached register values after raw port writes, AK4117 interrupt masking mistakes on edge-triggered PCMCIA IRQs, and races between suspend and IRQ/PCM handling. Useful signals are card probe/resume logs, AK4117 lock/rate reporting, proc FPGA revision output, capture start after suspend/resume, and absence of interrupt storms when digital input lock changes.
