# sources/distributed-fs/ceph-client/drivers/gpio/gpiolib-swnode.c

## Purpose
`gpiolib-swnode.c` implements GPIO lookup and counting for software-node firmware descriptions. It lets software nodes reference GPIO controllers and line flags using generic property APIs, including a special undefined GPIO node for bindings such as internal SPI chip selects.

## Important APIs, Types, And Functions
The main exported-to-gpiolib helpers are `swnode_find_gpio()` and `swnode_gpio_count()`. Internal helpers are `swnode_get_gpio_device()` and `swnode_gpio_get_reference()`. When `CONFIG_GPIO_SWNODE_UNDEFINED` is enabled, it exports `swnode_gpio_undefined` in the `GPIO_SWNODE` namespace and registers/unregisters it at subsystem init/exit.

## Control Flow
`swnode_find_gpio()` verifies the consumer fwnode is a software node, tries standard GPIO property names, handles `-ENOTCONN` as `-EPROBE_DEFER` for not-yet-registered remote software nodes, resolves the referenced GPIO device by fwnode or legacy label fallback, retrieves the descriptor by offset, and returns native GPIO flags from the second argument.

`swnode_gpio_count()` loops over standard property names and counts references by repeatedly calling `fwnode_property_get_reference_args()` with two expected arguments.

## State And Persistence
The file owns little runtime state beyond the optional globally registered `swnode_gpio_undefined`. Lookup uses temporary fwnode references and drops them after descriptor resolution. The code has a FIXME noting that the GPIO device ref is put while returning a descriptor, mirroring lifetime concerns in other firmware lookup paths.

## Dependencies And Integration Points
It depends on software nodes, generic property APIs, GPIO consumer/driver/property interfaces, fwnode matching, and gpiolib descriptor lookup. It integrates software-node-described devices with the generic `gpiod_get()` firmware lookup path.

## Risks
The label fallback is explicitly a compatibility workaround for software nodes not actually attached to GPIO controllers, so it can mask bad modeling. Reference lifetime is subtle because descriptors outlive the local GPIO device reference. The code assumes software-node GPIO references use exactly two args: offset and native flags.

## Test Signals
Test valid software-node GPIO lookups, missing properties, undefined GPIO sentinel returning not-found, remote node not registered returning probe defer, label fallback, multi-GPIO counting, and native flag propagation.
