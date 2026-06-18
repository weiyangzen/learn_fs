<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-kempld.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-kempld.c

## Purpose
`gpio-kempld.c` provides GPIO and optional interrupt support for Kontron PLD devices compatible with KEMPLD spec revision 2.0 or later.

## Important APIs, types, and functions
`struct kempld_gpio_data` stores the gpiochip, parent PLD pointer, selected output-level register, IRQ mutex, and cached IRQ enable/type registers. GPIO helpers include bit operations, get/set multiple, direction, and dynamic pin-count detection. IRQ helpers include mask/unmask, type setup, bus lock/sync, threaded parent handler, and `kempld_gpio_irq_init()`.

## Control flow
Probe validates PLD spec revision, chooses the output register based on spec version, sets platform or dynamic base, detects pin count by probing the event register, initializes optional IRQ support from BIOS-configured or module-overridden IRQ, then registers the gpiochip. IRQ bus sync writes cached edge/level, polarity, and enable registers; the threaded handler reads and clears status then handles nested child IRQs.

## State and persistence behavior
GPIO state lives in PLD registers. IRQ configuration is cached in `ien`, `evt_low_high`, and `evt_lvl_edge` and flushed during irq bus unlock. Pin count is inferred at probe and fixed for runtime.

## Dependencies and integration points
The driver depends on the KEMPLD MFD, its shared mutex helpers and register accessors, optional platform `gpio_base`, and optional module parameter `gpio_irq`.

## Risks and edge cases
Pin-count detection temporarily clears and restores the event register, which can disturb preconfigured events if locking or ordering is wrong. IRQ override can conflict with platform routing. Older PLD specs are rejected; missing IRQ configuration silently disables interrupt support.

## Test signals
Test pin-count detection, spec-version output-register selection, get/set multiple register batching, input/output direction, all four IRQ trigger types, BIOS IRQ and module override paths, and nested threaded IRQ handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-kempld.c -->
