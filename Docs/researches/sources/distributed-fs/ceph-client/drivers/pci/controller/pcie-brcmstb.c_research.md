# sources/distributed-fs/ceph-client/drivers/pci/controller/pcie-brcmstb.c

## Purpose

`pcie-brcmstb.c` is the Broadcom STB/Raspberry Pi style PCIe Root Complex platform driver. It brings a Broadcom controller from reset into RC mode, programs outbound and inbound address translation, starts the downstream link, optionally exposes an internal MSI parent domain, handles downstream device regulators, supports suspend/resume, and can dump controller outbound-error registers during die/panic notifiers on SoCs that advertise error reporting.

## Important APIs, Types, And Functions

- `struct brcm_pcie` is the main runtime state: MMIO base, optional clock, DT node, link generation limit, MSI target address, reset controls, RESCAL reset, memory-controller sizes, subdevice regulators, SoC config, bridge reset state, and notifier/lock state.
- `struct pcie_cfg_data` is the SoC descriptor. It selects register offsets, SoC family, PERST and bridge reset callbacks, inbound-window count, optional PHY handling, optional post-setup hook, and error-report support.
- `struct brcm_msi` owns internal MSI state: IRQ domains, bitmap allocator, target address, chained IRQ, legacy/non-legacy register layout, and interrupt register base.
- `brcm_pcie_probe()` allocates a `pci_host_bridge`, maps registers, gets clocks/resets, powers PHY/reset blocks, calls `brcm_pcie_setup()`, configures MSI, registers the host bridge, and optionally registers panic/die notifiers.
- `brcm_pcie_setup()` is the central hardware setup path. It resets the bridge, clears SerDes IDDQ, configures burst/read behavior, computes inbound windows from `dma-ranges`, programs outbound windows from host resources, sets RC class code, applies link capability overrides, and calls the SoC post-setup hook.
- `brcm_pcie_start_link()` deasserts PERST, waits for PHY/data-link active, configures CLKREQ/L1SS policy, optionally enables SSC through MDIO, and logs negotiated link speed/width.
- `brcm_pcie_map_bus()` and `brcm7425_pcie_map_bus()` provide config-space access using RC-local registers for bus 0 and indexed external config windows for downstream buses.
- `brcm_pcie_enable_msi()`, `brcm_allocate_domains()`, `brcm_pcie_msi_isr()`, and `brcm_msi_set_regs()` implement the MSI parent domain and hardware MSI registers.
- `brcm_pcie_suspend_noirq()` and `brcm_pcie_resume_noirq()` quiesce the link, power/reset blocks, regulators, clocks, and MSI registers across system sleep.
- `brcm_pcie_dump_err()` reads and clears outbound config/memory error registers under `bridge_lock` and reports decoded error data during panic/die notifications.

## Control Flow

Probe starts with `devm_pci_alloc_host_bridge()`, OF match data lookup, `devm_platform_ioremap_resource()`, optional `sw_pcie` clock, optional reset controls (`rescal`, `perst`, `bridge`, `swinit`), and `clk_prepare_enable()`. The bridge is deasserted early so registers are accessible, optional `swinit` is pulsed, RESCAL is reset, optional PHY is started, and `brcm_pcie_setup()` initializes controller translation and RC identity. After setup, hardware revision gates unsupported BCM4908 revisions. If MSI is enabled and the controller is its own `msi-parent`, the internal MSI domain is created. The `pci_host_bridge` receives Broadcom config ops and `pci_host_probe()` enumerates the bus; a post-probe link check rejects a link that dropped during scan.

Normal config access avoids CPU aborts by returning `NULL` for downstream config cycles when the link is down. RC config cycles use the controller register block directly. For downstream devices the driver writes an ECAM-derived index and returns the data window.

Power management shuts down in reverse: request L23 when linked, assert PERST, clear L23 request, set SerDes IDDQ, optionally assert bridge reset, stop PHY, rearm RESCAL, disable downstream regulators unless a child device can wake the system, and disable the clock. Resume re-enables the clock, resets RESCAL, starts PHY, deasserts bridge reset, reruns setup, re-enables regulators when needed, restarts the link, and restores MSI registers.

## State And Persistence

The driver persists only kernel runtime state and hardware register state. `bridge_in_reset` mirrors bridge reset state for panic-safe error dumping. `pcie->sr` stores downstream regulator handles acquired during `add_bus` and released during `remove_bus`. `ep_wakeup_capable` records a suspend-time decision to keep regulators enabled for wake-capable endpoints. MSI allocation is tracked in the `brcm_msi.used` bitmap under a mutex. Inbound memory-controller sizing is derived from `dma-ranges` and optional `brcm,scb-sizes` every setup/resume; outbound and inbound windows are reprogrammed on resume.

## Dependencies And Integration Points

The driver integrates with OF platform binding (`brcm,bcm2711-pcie`, `brcm,bcm2712-pcie`, `brcm,bcm4908-pcie`, `brcm,bcm7216-pcie`, and related compatibles), the PCI host bridge core, generic config accessors, reset and clock frameworks, regulator framework for downstream supplies, PHY/RESCAL reset controls, MSI irqdomain/`irq-msi-lib`, chained IRQ handling, panic/die notifier chains, and DT properties such as `dma-ranges`, `msi-parent`, `brcm,enable-ssc`, `brcm,clkreq-mode`, `aspm-no-l0s`, `num-lanes`, and `brcm,scb-sizes`.

## Risks And Edge Cases

- `brcm_pcie_get_inbound_wins()` has strict alignment and power-of-two assumptions. Bad or firmware-mutated `dma-ranges` can fail setup, and non-BCM7712 SoCs rely on inferred memory-controller size if `brcm,scb-sizes` is absent.
- Config-space access while link is down can cause CPU aborts, so link gating in `map_bus()` is a critical safety behavior.
- MSI target address selection depends on inbound window placement; devices requiring 32-bit MSI may fail if only the above-4G target is safe.
- CLKREQ/L1SS mode is DT-controlled and documented as capable of hanging traffic if misconfigured with an incompatible endpoint.
- Panic/die error dumping uses MMIO during exceptional paths and depends on `bridge_lock` plus `bridge_in_reset` to avoid accessing an off bridge.
- `CFG_QUIRK_AVOID_BRIDGE_SHUTDOWN` exists because some SoCs lose access to RESCAL or can hang fabric when a bridge is shut down.

## Test Signals

Useful validation includes successful platform probe, `pci_host_probe()` enumeration, expected "link up" speed/width logs, correct `lspci` bridge class, MSI allocation and interrupt delivery from endpoint devices, suspend/resume with and without wake-capable endpoints, regulator enable/disable behavior on root bus add/remove, DT variations for `dma-ranges`, `num-lanes`, `brcm,clkreq-mode`, and MSI parent, and injected link-down or bad-DT cases showing clean `-ENODEV`/`-EINVAL` failures rather than aborts.
