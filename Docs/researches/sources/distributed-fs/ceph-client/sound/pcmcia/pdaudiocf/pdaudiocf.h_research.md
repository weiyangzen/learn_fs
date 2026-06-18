# sources/distributed-fs/ceph-client/sound/pcmcia/pdaudiocf/pdaudiocf.h

Purpose: Defines PDAudioCF hardware register offsets, bit masks, chip status flags, the main `snd_pdacf` state structure, inline IO helpers, and cross-file function prototypes for the PDAudioCF driver.

Important APIs/types/functions: Register offsets describe music data, write/read data pointers, test control, status/control, interrupt status/enable, and AK interface. Bit masks cover FPGA/AKM/SRAM reset, powerdown, clock divider, recording, data detected, LED control, data format, FPGA revision, buffer/overrun/AKM IRQs, LED duty/modulation, and half-rate behavior. `struct snd_pdacf` stores ALSA card/index, IO port/IRQ, `reg_lock`, software register map, suspend SCR, AK4117 state/lock, chip status flags, PCM runtime/copy bookkeeping, and PCMCIA device pointer. `pdacf_reg_write()` updates the software regmap and writes a 16-bit IO register; `pdacf_reg_read()` reads a 16-bit IO register.

Control flow: No top-level executable flow, but the header defines how C files coordinate: card-service code creates/configures `snd_pdacf`, core code powers/reinitializes and creates AK4117, IRQ code services hardware interrupts, and PCM code uses the PCM fields for capture transfer accounting.

State and persistence: `regmap[]` mirrors writable hardware registers for restore and coordinated updates. `suspend_reg_scr` preserves SCR through PM. `chip_status` tracks stale/configured/suspended lifecycle. PCM fields persist while a stream is active and include format conversion flags, frame/sample sizes, total/period done counters, hardware pointer, and mapped area.

Dependencies/integration: Includes ALSA PCM and AK4117, Linux IO/IRQ, and PCMCIA CIS/device headers. Prototypes connect `pdaudiocf.c` with `pdaudiocf_core.c`, `pdaudiocf_irq.c`, and `pdaudiocf_pcm.c`.

Risks: IO helpers assume 16-bit port access and valid `reg >> 1` indexing into an eight-entry regmap; new registers must fit that model. Status bits gate hardware access after detach/suspend; callers must check stale/configured state. PCM bookkeeping is shared with IRQ/threaded paths, so lock and interrupt expectations in implementation files matter.

Test signals: Build all PDAudioCF objects, exercise register read/write paths, verify PM restores SCR/regmap, test AK4117 creation and interrupt handling, and run capture with different sample formats to validate PCM bookkeeping fields.
