# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/aiutils.c

Purpose: provides BCMA/AI chip utility support for brcmsmac, especially chipcommon discovery, clock-control setup, board/chip metadata access, and a 4313 external PA workaround.

Important APIs and functions: `ai_attach()` allocates `struct si_info` and calls `ai_doattach()` to populate public chip data from `bcma_bus`. `ai_detach()` frees it. `ai_cc_reg()` masks/sets chipcommon registers. `ai_clkctl_init()`, `ai_clkctl_fast_pwrup_delay()`, and `ai_clkctl_cc()` configure dynamic clock control and compute D11 fast wake delays. `ai_epa_4313war()` enables external PA GPIO control. `ai_deviceremoved()` checks PCI vendor ID disappearance.

Control flow: attach stores BCMA bus/PCI handles, chip ID/revision/package, board vendor/type, chipcommon revision/status/capabilities, PMU rev/caps, clears GPIO pullups/pulldowns, and measures ALP when PMU is present. Clock init uses chipcommon power-control capability, programs ILP divider to 1 MHz, then writes PLL/fref delay registers. Fast power-up delay uses PMU helper when available, otherwise derives a delay from slow-clock frequency and chipcommon registers.

State and persistence: `struct si_info` is heap state tied to driver lifetime. Hardware register writes persist until reset or later driver writes. No filesystem persistence.

Dependencies and integration: depends on Linux BCMA, PCI config access, chipcommon register offsets, PMU helpers, board/chip ID definitions, and brcmsmac public `si_pub` accessors.

Risks and test signals: incorrect clock delay math or capability detection can cause wake/PLL instability. `ai_deviceremoved()` only detects PCI-host removal. Test attach on supported BCMA chips, PMU and non-PMU paths, fast clock mode transitions, PCI hot removal, and 4313 EPA board behavior.
