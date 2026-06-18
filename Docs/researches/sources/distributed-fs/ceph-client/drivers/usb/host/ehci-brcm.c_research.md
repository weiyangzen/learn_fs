<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ehci-brcm.c -->
# sources/distributed-fs/ceph-client/drivers/usb/host/ehci-brcm.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/usb/host/ehci-brcm.c` is the Broadcom STB EHCI platform wrapper. It provides clock/resource setup, big-endian MMIO reset handling, Broadcom instruction-register workarounds, and a hub-control override that aligns resume completion to a microframe boundary. The source was read as a complete 281-line file.

## Important APIs, Types, and Functions

`struct brcm_priv` stores the optional clock. Key functions are `ehci_brcm_wait_for_sof()`, `ehci_brcm_hub_control()`, `ehci_brcm_reset()`, `ehci_brcm_probe()`, `ehci_brcm_remove()`, `ehci_brcm_suspend()`, and `ehci_brcm_resume()`. `brcm_overrides` replaces the generic reset routine and extends private storage; probe also assigns `ehci_brcm_hc_driver.hub_control`.

## Control Flow

Probe sets a 32-bit DMA mask, gets the IRQ, creates an HCD from the Broadcom-customized EHCI driver, enables an optional clock, maps MMIO, and calls `usb_add_hcd()`. Reset marks MMIO big-endian, derives operational register base from capabilities, issues a controller reset to avoid reboot lockups, writes two Broadcom instruction registers to avoid OUT underflows, and then calls common `ehci_setup()`. Hub control intercepts `GetPortStatus` when clearing a resume bit; it disables local IRQs, waits for the next SOF and an extra delay, then delegates to `ehci_hub_control()`. Suspend delegates to `ehci_suspend()` and gates the clock; resume ungates the clock, reapplies instruction-register tuning, calls `ehci_resume()`, and resets runtime-PM bookkeeping.

## State and Persistence Behavior

Persistent runtime state is the HCD and optional clock. Hardware-visible state includes big-endian register access, instruction-register tuning, and normal EHCI schedules/root hub state. No file-backed state exists.

## Dependencies and Integration Points

The driver matches `brcm,ehci-brcm-v2` and `brcm,bcm7445-ehci`, depends on the clock framework, platform resources, and common EHCI core. It integrates with the USB hub layer through the overridden `hub_control` path.

## Risks and Edge Cases

The SOF workaround runs with local IRQs disabled and uses atomic polling; excessive delay would affect interrupt latency. The hub-control override must remain compatible with generic EHCI hub semantics. Broadcom instruction-register magic values are hardware-specific and must be restored after resume. Big-endian MMIO assumptions are central to reset correctness.

## Test Signals

Validate resume from suspended ports near microframe boundaries, reboot/shutdown without controller lockup, high-memory bus-load OUT transfers, suspend/resume clock gating, and enumeration on both compatible strings. Dynamic debug logs should show SOF workaround only on matching resume-completion cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ehci-brcm.c -->
