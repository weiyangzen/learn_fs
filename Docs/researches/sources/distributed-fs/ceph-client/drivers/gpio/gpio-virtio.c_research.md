# sources/distributed-fs/ceph-client/drivers/gpio/gpio-virtio.c

## Purpose
Provides a virtio transport driver for virtual GPIO controllers. It exposes virtio GPIO lines through gpiolib and optionally maps virtio GPIO event queues into Linux IRQs when the device advertises `VIRTIO_GPIO_F_IRQ`.

## Important APIs, Types, And Functions
- `struct virtio_gpio_line` owns one preallocated request/response pair, line mutex, completion, and returned length.
- `struct vgpio_irq_line` tracks one interrupt event buffer plus type, disabled/masked, queued, and pending-update flags.
- `_virtio_gpio_req` is the synchronous virtqueue transaction primitive for all request-queue operations.
- `virtio_gpio_get_direction`, `virtio_gpio_direction_input`, `virtio_gpio_direction_output`, `virtio_gpio_get`, `virtio_gpio_set`, and `virtio_gpio_free` implement `gpio_chip` callbacks.
- IRQ support is split across `virtio_gpio_irq_prepare`, mask/unmask/enable/disable/set-type callbacks, `virtio_gpio_irq_bus_sync_unlock`, `ignore_irq`, and `virtio_gpio_event_vq`.
- `virtio_gpio_probe` reads virtio config, allocates line state, initializes optional irqchip state, allocates virtqueues, fetches line names, and registers the GPIO chip.

## Control Flow
GPIO operations lock the per-line buffer, populate a virtio GPIO request, add request and response scatterlists to `requestq` under the virtqueue mutex, kick the queue, wait for completion, then validate status and response length. Direction-output writes the value first, then switches direction. IRQ enable/type changes are staged in per-line flags under the IRQ bus lock; bus sync sends `VIRTIO_GPIO_MSG_IRQ_TYPE` and queues event buffers only after the backend has enabled the line. Event-queue completions validate the response length, derive the GPIO number from the returned buffer pointer, filter disabled or invalid events, and dispatch `generic_handle_domain_irq`.

## State And Persistence
State is entirely live virtio-device state: per-line request buffers, completions, IRQ type/mask/queued flags, and optional line-name strings returned by the device. The virtio backend owns the durable GPIO state. Removal unregisters the gpiochip and resets/deletes virtqueues.

## Dependencies And Integration Points
Depends on the virtio core, `uapi/linux/virtio_gpio.h`, scatterlist DMA semantics, gpiolib, and generic IRQ domains. The driver binds to `VIRTIO_ID_GPIO`, uses `virtio_find_vqs` for `requestq` and optional `eventq`, and publishes line names through `gc.names`.

## Risks And Edge Cases
The synchronous request path can hang if a backend never completes a request. IRQ state transitions are subtle because buffers cannot be queued while masked/disabled and invalid returned buffers must be requeued only when the line is enabled again. `virtio_gpio_get_names` trusts the config size but must guard against truncated name blocks; zero-length names are allowed. Virtqueue API serialization depends on `vgpio->lock`, while interrupt queueing uses a raw spinlock.

## Test Signals
Use a virtio-gpio device with and without IRQ feature support, verify request response status and length checks, line-name parsing with zero-length and truncated entries, direction-output ordering, IRQ enable/mask/unmask/type transitions, invalid event-buffer requeueing, and removal while no event buffers remain live.
