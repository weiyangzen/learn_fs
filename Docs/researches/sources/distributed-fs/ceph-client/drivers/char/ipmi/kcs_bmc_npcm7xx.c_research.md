<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ipmi/kcs_bmc_npcm7xx.c -->
# sources/distributed-fs/ceph-client/drivers/char/ipmi/kcs_bmc_npcm7xx.c

## Purpose
Implements the Nuvoton NPCM7xx hardware provider for BMC-side KCS channels. It maps per-channel registers through a parent syscon regmap, configures interrupts, enables channels, and registers with the generic KCS BMC core.

## Important APIs, Types, and Functions
- `struct npcm7xx_kcs_reg` describes status, data out, data in, control, and interrupt-enable register offsets.
- `struct npcm7xx_kcs_bmc` wraps `kcs_bmc_device`, regmap, and chosen register table entry.
- `npcm7xx_kcs_inb/outb/updateb()` implement provider register ops.
- `npcm7xx_kcs_enable_channel()` controls core IRQ enable bits.
- `npcm7xx_kcs_irq_mask_update()` controls IBF/OBE interrupt enables.
- `npcm7xx_kcs_probe()` parses `kcs_chan`, obtains regmap/IRQ, enables the channel, and registers it.

## Control Flow
Probe validates `kcs_chan` in range 1-3, allocates state, gets the parent syscon regmap, fills the generic device with channel-specific register offsets and ops, requests the platform IRQ, disables event masks, enables the channel, registers with KCS core, and logs offsets. IRQs call `kcs_bmc_handle_event()`. Remove unregisters then disables the channel and masks events.

## State and Persistence
Driver state is one `npcm7xx_kcs_bmc` per channel. Hardware interrupt enable and control bits persist while the channel is enabled.

## Dependencies and Integration Points
Matches OF compatible `nuvoton,npcm750-kcs-bmc`, depends on parent syscon regmap and generic KCS BMC core.

## Risks
Invalid or missing `kcs_chan` prevents probe. Unlike Aspeed, NPCM has hardware OBE interrupt bits, so event mask correctness depends directly on control register behavior. Removal order must avoid events after generic clients are removed.

## Test Signals
Probe channels 1-3, invalid channel values, IRQ request failure, IBF/OBE mask toggles, KCS client request/response through the generic cdev client, and remove/unload cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ipmi/kcs_bmc_npcm7xx.c -->
