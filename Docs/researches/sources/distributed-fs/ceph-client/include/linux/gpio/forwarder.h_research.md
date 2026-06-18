<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/gpio/forwarder.h -->
# sources/distributed-fs/ceph-client/include/linux/gpio/forwarder.h

Purpose: This header declares a GPIO forwarding abstraction: a synthetic `gpio_chip` can expose lines that forward operations to existing `gpio_desc` providers.

Important APIs/types/functions: `struct gpiochip_fwd` is opaque. Allocation and composition use `devm_gpiochip_fwd_alloc()`, `gpiochip_fwd_desc_add()`, and `gpiochip_fwd_desc_free()`. Publication uses `gpiochip_fwd_register()`, with `gpiochip_fwd_get_gpiochip()` and `gpiochip_fwd_get_data()` exposing the generated chip and caller data. Forwarded operation helpers mirror `gpio_chip` callbacks: request, get direction, direction input/output, get, get multiple, set, set multiple, set config, and to-IRQ.

Control flow, state, and persistence: Callers allocate a forwarding object for `ngpios`, attach descriptors at offsets, then register it. After registration, the helper callbacks translate chip offsets to stored descriptors and delegate operations to the underlying GPIO consumer/provider APIs. Lifetime is device-managed for allocation, but descriptor attachment/freeing is explicit.

Dependencies/integration: It depends on gpiolib descriptor semantics and the provider interface in `gpio/driver.h`. It is useful for MFD, aggregator, or board glue drivers that need to republish selected GPIO lines under a different controller.

Risks and test signals: Risks are stale descriptors, offset collisions, inconsistent `ngpios`, and forwarding IRQ/config operations to backing lines that do not support them. Tests should register a forwarder with valid and missing descriptors, validate direction/value propagation, error propagation, cleanup, and IRQ mapping behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/gpio/forwarder.h -->
