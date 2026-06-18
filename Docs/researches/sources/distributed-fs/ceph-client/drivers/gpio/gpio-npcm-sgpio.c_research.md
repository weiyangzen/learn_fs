<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-npcm-sgpio.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-npcm-sgpio.c

## Purpose
Nuvoton NPCM serial GPIO driver. It exposes output SGPIOs first and input SGPIOs after them, configures shift-clock and port counts, and provides IRQs for the input half only.

## Important APIs, types, and functions
`struct npcm_sgpio` stores the chip, clock, IRQ chip, lock, MMIO base, parent IRQ, input/output counts, port counts, and per-input IRQ type cache. `struct npcm_sgpio_bank` maps eight banks. GPIO callbacks are direction, get, and set functions. IRQ paths include valid-mask setup, mask/unmask, ack, set_type, and chained handler.

## Control flow
Probe reads `nuvoton,input-ngpios` and `nuvoton,output-ngpios`, validates each <=64, selects a shift-clock divisor from match data, programs `IOXCFG2`, clears event config/status, registers IRQs, registers the chip, and enables periodic scanning. Output offsets hit `WRITE_DATA`; input offsets subtract `nout_sgpio` and hit `READ_DATA`.

## State and persistence behavior
Persistent runtime state is line counts, port counts, selected clock configuration, and cached IRQ event type. Event masks/status live in hardware. No suspend/resume restore exists.

## Dependencies and integration points
Uses platform MMIO, OF compatibles `nuvoton,npcm750-sgpio` and `nuvoton,npcm845-sgpio`, peripheral clocks, gpiolib valid masks, and chained IRQs.

## Risks and edge cases
Input IRQ hwirqs must subtract the output count correctly. Type programming ORs new type bits into `EVENT_CFG`, so stale type bits can remain across direct type changes. Clock selection is sensitive to APB rate. Output writes are not lock-protected.

## Test signals
DT count parsing, port setup, shift-clock setup, output set/get, input get, IRQ valid-mask exclusion of outputs, and rising/falling/both status clearing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-npcm-sgpio.c -->
