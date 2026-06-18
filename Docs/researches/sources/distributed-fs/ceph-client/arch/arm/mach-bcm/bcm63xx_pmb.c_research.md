# sources/distributed-fs/ceph-client/arch/arm/mach-bcm/bcm63xx_pmb.c

Purpose: powers up BCM63138 secondary CPU domains through the Broadcom PMB/BPCM reset controller.

Important APIs/types/functions: internal `bpcm_wr_rd_mask()` polls BPCM state after writes; `bcm63xx_pmb_get_resources()` parses CPU hardware ID and reset phandle; exported-to-local `bcm63xx_pmb_power_on_cpu()` performs PLL, CPU, RAM, clamp, and reset sequencing.

Control flow: SMP code passes a CPU node. The PMB helper maps the reset controller, serializes access with `pmb_lock`, checks if reset is already deasserted, powers CPU and memory rails, waits for status bits, clears clamps, deasserts reset, unmaps, and returns status.

State and persistence: no permanent mapping; each call maps/unmaps PMB registers. Hardware power/reset state persists after the function returns.

Dependencies and integration: uses reset phandle format with two cells, `bpcm_rd()`/`bpcm_wr()` from the BCM63xx reset framework, and is called by `bcm63xx_smp.c`.

Risks: polling loops have no explicit timeout inside this helper; a failed power transition can spin indefinitely if BPCM never reports the expected bit. CPU IDs above one are only warned about, not rejected.

Test signals: BCM63138 SMP boot, PMB status register tracing, invalid `resets` phandle tests, and secondary CPU reset/power sequencing on real hardware.
