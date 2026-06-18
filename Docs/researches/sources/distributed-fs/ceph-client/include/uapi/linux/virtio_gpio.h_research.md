# sources/distributed-fs/ceph-client/include/uapi/linux/virtio_gpio.h

Purpose: defines the virtio GPIO controller ABI for line naming, direction/value operations, and optional GPIO interrupt delivery.

Important APIs/types/functions: feature bit `VIRTIO_GPIO_F_IRQ` gates IRQ support. Request types include get names, get/set direction, get/set value, and IRQ type. Status values are OK/ERR. Direction values are none/out/in. IRQ type values cover none, rising/falling/both edges, high/low levels. Structs include `virtio_gpio_config`, `virtio_gpio_request`, `virtio_gpio_response`, `virtio_gpio_response_get_names`, `virtio_gpio_irq_request`, and `virtio_gpio_irq_response`, plus IRQ status valid/invalid constants.

Control flow: the guest reads config to learn `ngpio` and name table size, fetches names with `GET_NAMES`, sends request/response operations for individual GPIO lines, and when IRQ support is negotiated configures line IRQ type and receives IRQ responses on the interrupt virtqueue.

State and persistence: runtime state includes per-line direction, output value, sampled input value, configured IRQ trigger type, and line names. The config space persists number of lines and name table size. Requests are stateless transactions except for set operations updating line state.

Dependencies and integration: includes `linux/types.h` and integrates with virtio transport, guest GPIO frameworks, host GPIO emulation or forwarding, and interrupt delivery paths.

Risks: GPIO numbers are 16-bit and must be range-checked against `ngpio`. `GET_NAMES` returns a flexible byte array sized by config, so parsers need length discipline. IRQ support is optional and must be feature-negotiated. Level and edge trigger constants are bit-like but should be interpreted according to the protocol.

Test signals: line enumeration/name tests, get/set direction and value round-trips, invalid GPIO number tests, IRQ feature negotiation tests, edge/level interrupt delivery tests, and ABI layout checks.
