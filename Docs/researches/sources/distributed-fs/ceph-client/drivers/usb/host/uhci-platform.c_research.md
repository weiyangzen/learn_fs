# sources/distributed-fs/ceph-client/drivers/usb/host/uhci-platform.c

## Purpose
`uhci-platform.c` provides generic MMIO platform-device glue for UHCI controllers, including device-tree-described generic/platform UHCI and ASpeed variants. It maps resources, sets DMA masks, handles optional clocks and reset controls, parses port/quirk data from DT, and registers the shared UHCI HCD.

## Important APIs, Types, And Functions
`uhci_platform_init()` sets generic reset/check callbacks, counts ports if DT did not provide them, disables bus-specific PM quirk callbacks, and calls `check_and_reset_hc()`. `uhci_platform_hc_driver` reuses shared UHCI operations with `HCD_MEMORY | HCD_DMA | HCD_USB11`. `uhci_hcd_platform_probe()` performs device setup: DMA mask coercion, HCD allocation, resource mapping, DT property parsing, optional clock enable, optional reset deassertion, IRQ lookup, and `usb_add_hcd()`. Remove asserts reset, disables clock, removes the HCD, and releases it. Shutdown calls `uhci_hc_died()`.

## Control Flow
Probe rejects disabled USB, chooses a 64-bit DMA mask if match data is present, creates the HCD, maps the first resource, stores `uhci->regs`, optionally reads `#ports`, detects ASpeed-compatible strings and sets `is_aspeed`, enables clock and reset resources, gets IRQ 0, and adds the HCD with shared IRQ. Error paths unwind reset, clock, and HCD allocation. The OF table matches `generic-uhci`, `platform-uhci`, and `aspeed,ast2700-uhci` with match data for 64-bit DMA.

## State And Persistence Behavior
State is runtime-only: mapped registers, optional `clk`, optional reset-control array, root-port count, and ASpeed flag in `struct uhci_hcd`. Remove and error paths assert resets and disable clocks. No state persists across unload.

## Dependencies And Integration Points
The file depends on platform devices, OF helpers, clock framework, reset framework, DMA mask APIs, and shared UHCI non-PCI register accessors. ASpeed support depends on `uhci-hcd.h` translating UHCI register offsets to ASpeed-specific MMIO offsets when `uhci->is_aspeed` is set. `MODULE_SOFTDEP("pre: ehci_platform")` mirrors companion-controller ordering.

## Risks And Edge Cases
DT `#ports` can override probing, so bad firmware can misrepresent the root hub. Only ASpeed AST2700 has match data for 64-bit DMA in this table, while older ASpeed compatibles enable only the workaround flag. Remove asserts reset before `usb_remove_hcd()`, which may quiesce hardware before usbcore teardown and should be reviewed against shared HCD expectations. Optional resets are requested shared, so board-level reset topology matters.

## Test Signals
Test generic and ASpeed DT binding, DMA mask selection, clock/reset error unwinds, IRQ sharing, port-count parsing, ASpeed register access, enumeration, suspend/resume if enabled, remove, and shutdown. Runtime logs should report DT port detection and ASpeed workaround enablement when applicable.
