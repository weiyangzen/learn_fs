# sources/distributed-fs/ceph-client/drivers/pwm/pwm-brcmstb.c

Purpose: implements the two-channel Broadcom STB/BCM7038 PWM controller.

Important APIs/types/functions: `struct brcmstb_pwm` stores MMIO base and clock. Endian-aware `brcmstb_pwm_readl/writel()` support big-endian MIPS. `brcmstb_pwm_config()` calculates variable-frequency control word, period, and on-time registers. `brcmstb_pwm_enable_set()` toggles start, output-enable, and open-drain bits. `brcmstb_pwm_apply()` restricts polarity and coordinates config/enable.

Control flow: probe gets the clock, maps MMIO, and registers two PWMs. Apply rejects inverted polarity, disables output if requested, otherwise computes configuration and enables the channel if it was previously off. Suspend disables the clock; resume reenables it.

State and persistence: no software cache beyond MMIO and clock. Hardware registers keep configuration while powered, but suspend only gates the clock and does not save registers.

Dependencies and integration: depends on common clock, platform/OF matching for `brcm,bcm7038-pwm`, MMIO, endian conditionals for MIPS, and PWM core callbacks.

Risks and test signals: duty equal to period uses a special 100 percent path. The variable-frequency control word search halves powers of two and can reject long periods. No readback callback exists. Test signals include normal-only polarity, 0/100 percent duty, long period rejection, big-endian register access, suspend/resume clock behavior, and two-channel independence.
