<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/gpio/gpio-utils.h -->
# sources/distributed-fs/ceph-client/tools/gpio/gpio-utils.h

Purpose: Declares the GPIO tool helper API and inline bit operations for GPIO v2 line value masks.

Important APIs/types/functions: Declares request/value/release APIs and one-shot get/set helpers. Defines `ARRAY_SIZE`, `check_prefix()`, and inline bit helpers `gpiotools_set_bit()`, `gpiotools_change_bit()`, `gpiotools_clear_bit()`, `gpiotools_test_bit()`, and `gpiotools_assign_bit()` over `__u64`.

Control flow: Header-only helpers perform direct bit manipulation using `_BITULL(n)` from Linux type/bit headers.

State and persistence: No persistent state; helpers mutate caller-provided mask/value words.

Dependencies/integration: Includes `<linux/types.h>` and relies on GPIO v2 structs from translation units that include `<linux/gpio.h>`. Shared by all GPIO C tools.

Risks/tests: Risks include undefined shifts for out-of-range bit indices and `check_prefix()` intentionally requiring the tested string to be longer than the prefix. Test signals are mask helper unit tests for indices 0 and max line count, prefix matching for `gpiochip`, and compiler coverage with current UAPI headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/gpio/gpio-utils.h -->
