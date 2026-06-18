# sources/distributed-fs/ceph-client/drivers/leds/blink/Makefile

## Purpose
This small Makefile maps blink LED Kconfig symbols to driver objects.

## Important APIs, Types, and Functions
The object mappings are `obj-$(CONFIG_LEDS_BCM63138) += leds-bcm63138.o` and `obj-$(CONFIG_LEDS_LGM) += leds-lgm-sso.o`.

## Control Flow
When the top-level LED Makefile descends into `blink/`, Kbuild evaluates these assignments and includes the relevant objects according to each tristate symbol.

## State and Persistence
There is no runtime state. The persistent effect is whether the two driver objects are compiled into the kernel tree or emitted as modules.

## Dependencies and Integration Points
The file depends on symbol definitions in `drivers/leds/blink/Kconfig` and source files in the same directory. It is reached unconditionally from the parent Makefile, but object inclusion remains conditional.

## Risks and Edge Cases
Any rename mismatch between Kconfig, Makefile, and source filenames breaks the selected driver build. Because the parent descends unconditionally, stale entries are caught in broad builds even if only as disabled references in review.

## Test Signals
Enable `CONFIG_LEDS_BCM63138=m` and `CONFIG_LEDS_LGM=m` and confirm `leds-bcm63138.ko` and `leds-lgm-sso.ko` are produced. `allmodconfig` should catch missing include dependencies in both objects.
