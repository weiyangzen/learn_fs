# sources/distributed-fs/ceph-client/drivers/pci/controller/pcie-mediatek-gen3.c

## Purpose

`pcie-mediatek-gen3.c` is the MediaTek/Airoha Gen3 PCIe Root Complex platform driver for newer single-controller hardware such as MT8192, MT8196, and EN7581. It powers and resets the controller/PHY, programs RC mode, link speed/width, address translation windows, INTx and MSI domains, downstream power-control devices, host bridge config access, and noirq suspend/resume.

## Important APIs, Types, And Functions

- `struct mtk_gen3_pcie` stores controller state: MMIO/physical base, resets, PHY, clocks, link parameters, IRQ domains, MSI sets, bitmaps, saved IRQ state, and SoC data.
- `struct mtk_gen3_pcie_pdata` supplies SoC-specific `power_up` callback, PHY reset names, optional system-clock-ready timing, and flags such as `SKIP_PCIE_RSTB`.
- `mtk_pcie_parse_port()` maps `pcie-mac`, gets reset controls, optional PHY, all clocks, and optional `num-lanes`.
- `mtk_pcie_power_up()` handles generic MT819x reset/PHY/clock/runtime-PM sequencing; `mtk_pcie_en7581_power_up()` handles Airoha EN7581-specific PBus setup, reset ordering, EQ presets, and clock-reset workaround.
- `mtk_pcie_startup_port()` sets RC mode, link speed/width, class code, INTx masking, DVFSRC behavior, MSI capture registers, ATR translation tables, downstream power, and link polling.
- `mtk_pcie_set_trans_table()` splits host bridge IO/MEM windows into up to eight power-of-two ATR windows.
- `mtk_pcie_init_irq_domains()`, `mtk_pcie_irq_handler()`, `mtk_pcie_msi_handler()`, and INTx/MSI chip/domain callbacks implement legacy and MSI interrupt delivery.
- `mtk_pcie_probe()` wires pwrctrl creation, IRQ setup, hardware setup, and `pci_host_probe()`.
- `mtk_pcie_suspend_noirq()` and `mtk_pcie_resume_noirq()` move the link to L2, save/restore IRQ registers, power down/up, and restart the port.

## Control Flow

Probe allocates a host bridge, stores SoC match data, creates IRQ domains/chained handler, creates PCI power-control devices, then parses and powers the controller. Setup parses resources before touching hardware, deasserts shared PHY resets to balance counts, calls the SoC power-up callback, optionally restricts max link speed from DT if the controller supports it, and starts the port. Startup programs controller capability and translation, powers endpoints, waits for link-up, and reports the LTSSM state on timeout. After successful setup, host bridge ops are installed and PCI scanning begins.

Interrupt flow enters a chained handler on the controller IRQ. INTx status bits are forwarded through a linear INTx domain using fasteoi semantics. MSI status bits select one of eight MSI sets; each set loops over enabled status bits and dispatches through the MSI bottom domain. MSI allocation uses a bitmap over 256 vectors and associates each vector with its owning `mtk_msi_set`.

## State And Persistence

The driver persists MSI vector allocation in `msi_irq_in_use`, saved top-level and per-set MSI enable registers across suspend, downstream power-control device state, and SoC-specific reset/clock state. Hardware ATR, MSI, INTx, and link registers are reprogrammed after power-up/resume. No disk persistence exists.

## Dependencies And Integration Points

It integrates with OF platform matching, PCI host bridge APIs, PCI pwrctrl, runtime PM, bulk clocks, reset controls, PHY framework, syscon/regmap for EN7581 PBus CSR, irqdomain/MSI parent library, chained IRQ handling, and DT properties/resources including `pcie-mac`, `num-lanes`, `max-link-speed`, `mediatek,pbus-csr`, `interrupt-controller`, and compatible-specific reset names.

## Risks And Edge Cases

- ATR translation has only eight entries and warns if resources exceed table capacity; unreachable resource tails may break endpoints.
- `mtk_pcie_probe()` has a `goto err_tear_down_irq; dev_err_probe(...)` ordering that makes the error log unreachable after pwrctrl creation failure.
- Link failure after endpoint power-up must unwind both endpoint power and controller power; EN7581 has a distinct reset path because normal PERST toggling is unsafe.
- MSI allocation uses contiguous bitmap regions and must keep set selection consistent for multi-MSI allocations.
- Suspend requires link transition to L2; failure aborts suspend.
- Invalid `num-lanes` is only warned and defaults to hardware behavior, which may hide DT mistakes.

## Test Signals

Validate probe on each compatible, pwrctrl creation/defer paths, EN7581 PBus programming, ATR programming for IO/MEM windows, max-link-speed and `num-lanes` DT handling, link timeout LTSSM logging, INTx and MSI interrupts across all sets, MSI masking/unmasking/ack, suspend/resume IRQ state restoration, endpoint power sequencing, and removal cleanup.
