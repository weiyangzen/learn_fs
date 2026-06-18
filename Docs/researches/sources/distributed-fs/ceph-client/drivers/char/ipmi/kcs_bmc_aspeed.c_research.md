<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ipmi/kcs_bmc_aspeed.c -->
# sources/distributed-fs/ceph-client/drivers/char/ipmi/kcs_bmc_aspeed.c

## Purpose
Implements the Aspeed AST2400/AST2500/AST2600 hardware provider for BMC-side KCS channels. It maps LPC register offsets through a syscon regmap, configures LPC I/O addresses and host/BMC interrupts, emulates output-buffer-empty events where hardware lacks an IRQ, and registers channels with the generic KCS BMC core.

## Important APIs, Types, and Functions
- `struct aspeed_kcs_bmc` wraps `struct kcs_bmc_device`, `regmap`, upstream SerIRQ configuration, and OBE polling timer state.
- Register helpers `aspeed_kcs_inb()`, `aspeed_kcs_outb()`, and `aspeed_kcs_updateb()` implement `kcs_bmc_device_ops`.
- `aspeed_kcs_set_address()` programs LPC address registers for channels 1-4.
- `aspeed_kcs_config_upstream_irq()` configures host-directed SerIRQ from `aspeed,lpc-interrupts`.
- `aspeed_kcs_irq_mask_update()` enables/disables IBF interrupts and emulates OBE with polling and a timer.
- `aspeed_kcs_probe()` parses DT, configures hardware, enables the channel, and calls `kcs_bmc_add_device()`.

## Control Flow
Probe validates the parent LPC compatible, identifies channel by matching DT register offsets, reads LPC I/O addresses, optionally configures upstream SerIRQ, obtains the parent syscon regmap, programs address registers, requests the downstream IRQ, disables event masks, enables the channel, and registers with the KCS core. IRQs dispatch directly to `kcs_bmc_handle_event()`. Removal unregisters, disables the channel and events, marks OBE timer removal, and deletes the timer.

## State and Persistence
Hardware state persists in LPC control/address/interrupt registers. Driver state persists in `aspeed_kcs_bmc`, especially upstream IRQ mode/id and OBE timer removal flag protected by a spinlock.

## Dependencies and Integration Points
Depends on OF bindings `aspeed,ast2400-kcs-bmc-v2`, `aspeed,ast2500-kcs-bmc-v2`, and `aspeed,ast2600-kcs-bmc`, parent LPC syscon compatibility, platform IRQ, and generic KCS BMC core.

## Risks
Address programming differs significantly by channel, and channel 3 only supports inferred status address. SerIRQ support has chip-revision quirks for channel 1. OBE emulation is race-sensitive: the client must do a race-free check after enabling events, while the driver uses a short atomic poll then a slower timer. Removal must prevent timer rearming.

## Test Signals
Device-tree validation for all channels, one- and two-address configurations, invalid addresses, upstream IRQ modes and IDs, IBF IRQ delivery, OBE timer behavior, and remove while OBE timer is pending.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ipmi/kcs_bmc_aspeed.c -->
