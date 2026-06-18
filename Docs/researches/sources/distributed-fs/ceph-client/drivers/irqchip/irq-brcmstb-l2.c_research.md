# sources/distributed-fs/ceph-client/drivers/irqchip/irq-brcmstb-l2.c

## Purpose
Implements generic Broadcom STB Level 2 interrupt controllers in edge-latched and level-sensitive variants.

## Important APIs, Types, and Functions
`struct brcmstb_intc_init_params` describes register layout and flow handler. `l2_edge_intc_init` and `l2_lvl_intc_init` select edge/level behavior. `struct brcmstb_l2_intc_data` stores domain, generic chip, status/mask offsets, wake flag, and saved mask. Probe variants call `brcmstb_l2_intc_probe()`.

## Control Flow
Probe maps MMIO, masks all interrupts, optionally clears latched status, maps the parent IRQ, creates a 32-entry generic-chip domain, installs the chained handler, configures ack/mask/unmask register callbacks by variant, and enables wake support when DT allows. The chained handler reads status AND not-mask-status, dispatches all set bits, and uses a write barrier before returning to the parent.

## State and Persistence
Generic-chip hardware state is the mask register plus optional clear/ack register. `saved_mask` preserves masks across suspend. `wake_active` from generic irqchip determines suspend-time unmasking.

## Dependencies and Integration Points
Depends on platform irqchip registration, OF parent IRQ/address parsing, generic irqchip, and chained IRQ helpers. It integrates with Broadcom STB device tree compatibles for multiple L2 blocks.

## Risks and Test Signals
Risks include wrong variant register layout, bad IRQ if parent fires with no child status, wake mask mishandling, and edge status loss if cleared incorrectly on cold boot. Test signals are per-compatible registration, edge and level interrupt delivery, suspend/resume mask restoration, and absence of `handle_bad_irq` reports under normal operation.
