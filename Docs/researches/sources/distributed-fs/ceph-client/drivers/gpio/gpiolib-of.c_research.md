# sources/distributed-fs/ceph-client/drivers/gpio/gpiolib-of.c

## Purpose
`gpiolib-of.c` implements Device Tree GPIO integration. It counts GPIO properties, parses GPIO phandles, maps controller-specific GPIO specifiers to descriptors and Linux lookup flags, applies legacy naming and polarity quirks, manages dynamic gpio-hog additions/removals, provides default two-cell and three-cell translators, and registers pinctrl GPIO ranges from DT.

## Important APIs, Types, And Functions
Externally used functions include `of_gpio_count()`, `of_find_gpio()`, `of_gpiochip_get_lflags()`, `of_gpiochip_add()`, `of_gpiochip_remove()`, and `of_gpiochip_instance_match()`. With dynamic OF enabled, `gpio_of_notifier` handles reconfiguration events.

Important internal helpers are `of_get_named_gpiod_flags()`, `of_find_gpio_device_by_xlate()`, `of_xlate_and_get_gpiod_flags()`, `of_convert_gpio_flags()`, `of_gpio_flags_quirks()`, `of_find_gpio_rename()`, `of_find_trigger_gpio()`, `of_gpio_twocell_xlate()`, `of_gpio_threecell_xlate()`, and `of_gpiochip_add_pin_range()`.

## Control Flow
Consumer lookup through `of_find_gpio()` first tries standard property names produced by `for_each_gpio_property_name()`, such as `foo-gpios` and `foo-gpio`. If not found, it tries compatibility quirks for legacy names and trigger-source handling. Successful parsing uses `of_parse_phandle_with_args_map()`, finds a registered GPIO device whose chip node and `.of_xlate()` can translate the specifier, gets the descriptor, applies quirks, and converts OF flags into gpiolib lookup flags.

Counting uses `of_gpio_count()`, including a special SPI chip-select fallback for old Freescale/PPC bindings that used plain `gpios`. GPIO chip add sets default `.of_xlate` if the driver did not provide one, validates `of_gpio_n_cells`, adds pin ranges, takes a reference on the DT node, and marks gpio-hog children populated. Removal clears hog populated flags and puts the node.

With `CONFIG_OF_DYNAMIC`, `of_gpio_notify()` responds to added or removed gpio-hog nodes by finding the parent gpiochip and adding or removing hog descriptors.

## State And Persistence
The file mostly operates statelessly on DT data and gpiochip state. Persistent effects include node references held while a gpiochip is registered, populated flags on gpio-hog child nodes, pin ranges installed on gpiochips, and descriptor hog ownership created from DT.

## Dependencies And Integration Points
It depends on OF core parsing, OF dynamic reconfiguration, GPIO descriptor/chip APIs, pinctrl range APIs, firmware-node helpers, and numerous optional subsystem config symbols that enable compatibility quirks. It integrates DT bindings with generic `gpiod_get()` lookup paths and gpiochip registration.

## Risks
The compatibility quirk matrix is broad and config-dependent. Incorrect polarity override can invert hardware behavior. Dynamic hog handling only supports whole-node add/remove, not arbitrary modification. Three-cell translation depends on correct `of_node_instance_match()`. Pinctrl range parsing can defer probe if the pinctrl provider is not ready.

## Test Signals
Test standard `*-gpios` lookup, legacy renamed properties, SPI chip-select quirks, regulator and reset polarity overrides, trigger-source lookup, two-cell and three-cell controllers, invalid phandle args, deferred gpiochip registration, dynamic gpio-hog add/remove, pinctrl numeric and group ranges, and gpiochip unregister cleanup.
