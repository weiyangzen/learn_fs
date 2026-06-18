# sources/distributed-fs/ceph-client/drivers/iio/adc/Makefile

Purpose: kernel build mapping from ADC Kconfig symbols to objects in `drivers/iio/adc`.

Important APIs/types/functions: contains `obj-$(CONFIG_...) += ...` assignments for each ADC driver or helper object. Relevant subset entries are `obj-$(CONFIG_88PM886_GPADC) += 88pm886-gpadc.o`, `obj-$(CONFIG_AB8500_GPADC) += ab8500-gpadc.o`, and `obj-$(CONFIG_AD4000) += ad4000.o`. Some symbols build multiple objects, such as LTC2496/LTC2497 sharing `ltc2497-core.o`, and Xilinx XADC using a composite `xilinx-xadc-y`.

Control flow: no runtime flow. During kbuild, enabled or modular config symbols expand into built-in or module object lists. The list is intended to remain alphabetically ordered when adding entries.

State and persistence behavior: no state beyond build outputs. The file determines which `.o` files are linked into vmlinux or modules.

Dependencies and integration points: paired with `Kconfig` symbols and source files in the same directory. It also integrates composite object definitions for multi-file drivers.

Risks: missing or misspelled object mappings make a visible Kconfig option build nothing or fail late. A mismatch between Kconfig help module names and object names confuses users. Shared-core object mappings must include all required objects under each dependent symbol.

Test signals: run targeted builds for `CONFIG_88PM886_GPADC`, `CONFIG_AB8500_GPADC`, and `CONFIG_AD4000` as built-in/module where applicable; run `make drivers/iio/adc/`; and verify new Kconfig entries have matching Makefile objects in alphabetical order.
