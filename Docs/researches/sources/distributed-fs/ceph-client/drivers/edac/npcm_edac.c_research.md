# sources/distributed-fs/ceph-client/drivers/edac/npcm_edac.c

## Purpose
Provides EDAC memory-controller support for Nuvoton NPCM7xx and NPCM8xx SoCs. It reports correctable and uncorrectable DDR ECC interrupts, exposes NPCM8xx debugfs error injection when EDAC debug is enabled, and handles chip-specific register offsets through platform data.

## Important APIs, Types, And Functions
- `struct npcm_platform_data` captures per-chip register offsets, masks, and shifts.
- `struct priv_data` stores the MMIO base, platform data, message buffer, debugfs root, and injection settings.
- `handle_ce` and `handle_ue` read captured address/data/source/syndrome registers and call `edac_mc_handle_error`.
- `edac_ecc_isr` dispatches CE or UE status and acknowledges the matching interrupt.
- `force_ecc_error` writes syndrome injection controls on NPCM8xx and triggers a forced write check.
- `edac_probe` maps registers, initializes the regmap, validates ECC enablement, allocates the EDAC MC, requests IRQ, and registers with the EDAC core.

## Control Flow
Probe maps the memory-controller resource, creates a 32-bit regmap, obtains OF match data, and rejects hardware with ECC disabled. It forces interrupt mode, allocates a single all-memory EDAC layer, fills EDAC capabilities, requests the ECC IRQ, unmasks ECC events, adds the memory controller, and optionally creates debugfs injection files for NPCM8xx. Interrupt handling reads `ctl_int_status`; CE has priority over UE in the `if/else` chain, and each handled interrupt reads captured metadata, reports one event, writes the matching ACK mask, and returns `IRQ_HANDLED`.

## State And Persistence
`npcm_regmap` is a file-scope pointer initialized per probed device. Per-controller state is in `priv_data` attached to `mci->pvt_info`. Hardware interrupt masks and ECC enable bits persist in controller registers; remove deletes debugfs and EDAC MC state, masks master interrupts globally, and clears ECC enable bits.

## Dependencies And Integration Points
Depends on OF match data, platform IRQ resources, MMIO regmap, EDAC MC APIs, EDAC debugfs helpers, and Nuvoton memory-controller register layouts. It integrates with the EDAC core as a `mem_ctl_info` driver with DDR4 and SECDED capability.

## Risks And Edge Cases
The global `npcm_regmap` makes multiple simultaneous controllers unsafe unless the platform has only one instance. The ISR handles CE before UE and does not process both if both status bits are set. Remove disables ECC, which is a strong hardware policy decision. Injection accepts debugfs byte values and performs range checks only inside `force_ecc_error`; invalid requests return `count` after logging rather than an error.

## Test Signals
Exercise NPCM750 and NPCM845 OF matches, ECC-disabled probe rejection, CE and UE interrupts with captured high/low address fields, simultaneous CE/UE status behavior, interrupt masking after setup/remove, and debugfs injection for data and checkcode CE plus UE.
