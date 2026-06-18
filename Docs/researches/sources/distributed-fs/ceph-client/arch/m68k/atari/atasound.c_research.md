# sources/distributed-fs/ceph-client/arch/m68k/atari/atasound.c

Purpose: low-level Atari PSG/MICROWIRE sound helpers used for system beep and LM1992 control.

Important APIs are `atari_microwire_cmd(int cmd)` and `atari_mksound(unsigned int hz, unsigned int ticks)`. `atari_microwire_cmd()` writes the LM1992 address plus command to `tt_microwire`, then busy-waits until the mask returns to idle. `atari_mksound()` programs YM2149 generator A frequency, mixer, volume, and optional envelope length.

Control flow disables generator A, clamps the PSG period to 12 bits, writes period low/high registers, chooses either envelope-driven duration or fixed max volume, then re-enables generator A. Local IRQs are disabled while YM registers are selected and written.

State is YM2149 register selection/data, MICROWIRE registers, and no software timer. For finite `ticks`, the PSG envelope hardware determines sound length.

Dependencies include `asm/atarihw.h`, `atari.h`, `HZ`, and machine hook assignment in `config_atari()` when `CONFIG_INPUT_M68K_BEEP` is enabled.

Risks and test signals: busy-waiting MICROWIRE can hang if hardware is absent/misdetected; YM register select/write sequences are not self-describing and require IRQ protection. Test console bell, zero-frequency silence, long tick clamping, and MICROWIRE PSG enable during IRQ initialization.
