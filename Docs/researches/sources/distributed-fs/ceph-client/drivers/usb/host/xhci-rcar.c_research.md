# sources/distributed-fs/ceph-client/drivers/usb/host/xhci-rcar.c

## Purpose
Implements the Renesas R-Car and RZ platform xHCI wrapper. It provides firmware download and startup hooks for R-Car Gen2/Gen3, start/reset hooks for RZ/G3E and RZ/V2M, SoC match data, and a platform driver that delegates generic HCD work to `xhci_plat_probe()`.

## Important APIs, Types, And Functions
Key helpers are `xhci_rcar_start_gen2()`, `xhci_rcar_start()`, `xhci_rcar_download_firmware()`, `xhci_rcar_wait_for_pll_active()`, `xhci_rcar_init_quirk()`, and `xhci_rcar_resume_quirk()`. RZ/G3E helpers are `xhci_rzg3e_start()`, `xhci_rzg3e_suspend()`, `xhci_rzg3e_resume()`, and `xhci_rzg3e_post_resume()`. Match-data objects are `xhci_plat_renesas_rcar_gen2`, `xhci_plat_renesas_rcar_gen3`, `xhci_plat_renesas_rzv2m`, and `xhci_plat_renesas_rzg3e`.

## Control Flow
Probe gets OF match data and calls `xhci_plat_probe()`. For R-Car, the platform init quirk waits for PLL active and downloads firmware unless already successful. Firmware download requests the selected `.dlmem`, enables download mode, packs bytes into big-endian-style dwords written to `FW_DATA0`, sets the data-ready bit, polls until hardware clears it, disables download mode, and polls success. Start enables wrapper interrupts and, for Gen2, writes LCLK/configuration/polarity values. Resume re-downloads firmware if needed and restarts the wrapper. RZ/G3E start writes pipe settings and interrupt enables, with suspend/resume asserting/deasserting reset around generic xHCI PM.

## State And Persistence
State lives in wrapper MMIO registers, firmware-loaded controller RAM, reset state, and `struct xhci_plat_priv` match data. R-Car firmware is not durable across power/reset unless hardware keeps it loaded; the driver explicitly rechecks on init/resume. The driver stores no separate private object beyond generic platform xHCI state.

## Dependencies And Integration Points
Depends on firmware loader, MMIO polling, OF platform matching, reset controls, `xhci-plat.h`, `xhci-rcar-regs.h`, `xhci-rzg3e-regs.h`, and optional RZ/V2M helper declarations. It integrates with generic platform xHCI via callback hooks rather than direct HCD registration.

## Risks And Test Signals
Risks include firmware missing or malformed, atomic polling timeouts, byte packing mistakes for non-4-byte firmware tails, reset ordering on RZ/G3E, Gen2/Gen3 firmware mismatch, and 32-bit DMA/slow suspend quirk regressions. Test signals include all Renesas compatibles probing, firmware load logs, USB2/USB3 enumeration, Gen2 polarity/config behavior, RZ/G3E suspend/resume with reset, restore from hibernate, and missing firmware failure handling.
