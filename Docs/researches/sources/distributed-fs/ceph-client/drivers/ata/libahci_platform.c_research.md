# sources/distributed-fs/ceph-client/drivers/ata/libahci_platform.c

## Purpose
`libahci_platform.c` is the common platform-device resource and lifecycle layer for AHCI controllers that are not plain PCI AHCI devices. It discovers firmware-described MMIO, clocks, regulators, resets, PHYs, port child nodes, and platform capability overrides, sequences those resources safely, and then invokes `libahci.c` to initialize and activate the ATA host.

## Important APIs, Types, And Functions
The file exports `ahci_platform_ops`, which inherits `ahci_ops` and overrides `host_stop` so platform-managed resources are disabled on host teardown. Exported resource helpers include `ahci_platform_enable_phys()`, `ahci_platform_disable_phys()`, `ahci_platform_find_clk()`, `ahci_platform_enable_clks()`, `ahci_platform_disable_clks()`, `ahci_platform_deassert_rsts()`, `ahci_platform_assert_rsts()`, `ahci_platform_enable_regulators()`, `ahci_platform_disable_regulators()`, `ahci_platform_enable_resources()`, `ahci_platform_disable_resources()`, `ahci_platform_get_resources()`, `ahci_platform_init_host()`, `ahci_platform_shutdown()`, and PM helpers under `CONFIG_PM_SLEEP`.

Private helpers discover per-port PHYs/regulators, parse firmware properties (`hba-cap`, `ports-implemented`, `hba-port-cap`), find the maximum DT port id, and release manually acquired target regulators through a devres callback.

## Control Flow
`ahci_platform_get_resources()` opens a devres group, computes the number of ports from DT child `reg` values, allocates `ahci_host_priv` with room for PHY pointers, maps the AHCI MMIO resource, obtains clocks in bulk or falls back to one optional clock, obtains controller and PHY regulators, optionally obtains reset arrays, allocates non-devm target regulator storage, and walks child nodes. For each enabled child node it validates the port id, optionally creates/finds a child platform device to get the target regulator, gets the port PHY, and builds a mask of enabled ports. With no child nodes, it keeps compatibility by probing port 0 resources from the parent node. Firmware overrides are read, runtime PM is enabled and acquired, and the devres group is retained on success or released atomically on failure.

Resource enabling is ordered regulators, clocks, resets, PHYs; failures unwind in reverse. Disabling reverses that order. PHY enable initializes each non-ignored PHY, sets SATA mode, powers it on, and unwinds previously enabled PHYs if a later port fails. Regulator enable handles controller, PHY, and per-port target regulators with reverse-order cleanup.

`ahci_platform_init_host()` obtains IRQ 0, saves AHCI initial config, derives ATA flags for NCQ/PMP/EM, allocates an ATA host sized by CAP.NP and port map, configures parallel scan based on SSS, tags each port with MMIO descriptions, dummy-disables ports outside the implemented map, coerces 64-bit DMA if supported, resets and initializes the controller, prints AHCI info, and calls `ahci_host_activate()`. Shutdown freezes/stops each port and clears host interrupts to make kexec safe. Suspend/resume helpers disable/enable interrupts, host state, PHYs, resources, and runtime PM state in the expected order.

## State And Persistence
Runtime state is stored in `ahci_host_priv`: MMIO base, IRQ, clocks, regulators, resets, PHY pointers, target power regulators, firmware-supplied capability/port-map overrides, port masks, and a `got_runtime_pm` flag. Device-tree child nodes and regulator references drive per-port state. No durable state is written; hardware resources are enabled/disabled and AHCI register state is initialized by `libahci`.

## Dependencies And Integration Points
The file depends on platform devices, OF/device-tree APIs, clocks, regulators, reset controllers, generic PHY, runtime PM, DMA masks, libata, and `libahci.c` exported helpers. Board-specific AHCI platform drivers typically call `ahci_platform_get_resources()`, `ahci_platform_enable_resources()`, and `ahci_platform_init_host()` from probe and reuse the exported PM/shutdown helpers.

## Risks And Edge Cases
Resource ordering is safety-critical: PHYs should not power on before regulators/clocks/resets are ready, and error unwinds must not leave power rails active. Child-node port ids beyond allocated `nports` are warned and ignored; too many child nodes fail probe. Target regulators are not devm-managed because they belong to child devices, so the devres release callback must run. `pm_runtime_get_sync()` return is not explicitly checked, so platforms with runtime-PM failures need scrutiny. Firmware overrides can mask ports or capabilities incorrectly. Suspend with `AHCI_HFLAG_NO_SUSPEND` fails intentionally to avoid corrupt firmware behavior.

## Test Signals
Useful validation includes DTs with no child ports, sparse child port IDs, invalid IDs, disabled children, per-port regulators, missing optional clocks, deferred PHY/regulator probes, reset-trigger versus reset-assert semantics, resource-enable failure injection at each stage, 64-bit DMA coercion, dummy disabled ports, SSS parallel-scan behavior, kexec shutdown with interrupts cleared, system suspend/resume, and runtime PM state after resume.
