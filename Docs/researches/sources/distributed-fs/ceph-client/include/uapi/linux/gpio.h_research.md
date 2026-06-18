<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/gpio.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/gpio.h

## Purpose
`gpio.h` defines the userspace ABI for GPIO character devices. It covers chip information, line information, line requests, event delivery, value get/set, reconfiguration, and the deprecated v1 ABI retained for compatibility.

## Important APIs, types, and functions
The v2 ABI centers on `struct gpiochip_info`, `enum gpio_v2_line_flag`, `struct gpio_v2_line_values`, `enum gpio_v2_line_attr_id`, `struct gpio_v2_line_attribute`, `struct gpio_v2_line_config_attribute`, `struct gpio_v2_line_config`, `struct gpio_v2_line_request`, `struct gpio_v2_line_info`, `struct gpio_v2_line_info_changed`, and `struct gpio_v2_line_event`. V2 ioctls include `GPIO_GET_CHIPINFO_IOCTL`, `GPIO_V2_GET_LINEINFO_IOCTL`, `GPIO_V2_GET_LINEINFO_WATCH_IOCTL`, `GPIO_V2_GET_LINE_IOCTL`, `GPIO_V2_LINE_SET_CONFIG_IOCTL`, `GPIO_V2_LINE_GET_VALUES_IOCTL`, `GPIO_V2_LINE_SET_VALUES_IOCTL`, and line-info unwatch. V1 exposes `gpioline_info`, `gpiohandle_request`, `gpiohandle_config`, `gpiohandle_data`, `gpioevent_request`, and `gpioevent_data`.

## Control flow
Users open a gpiochip device, fetch chip/line metadata, request one or more line offsets with a `gpio_v2_line_config`, receive an anonymous request fd, then read edge events or issue get/set/reconfigure ioctls on that fd. Line info watch produces change events when request, release, or config state changes.

## State and persistence behavior
Chip and line metadata is live kernel state. A successful line request persists ownership, consumer label, direction, bias, drive, active-low, edge, debounce, event clock, and event buffer state until the request fd closes or config changes. Events carry monotonic, realtime, or HTE timestamps and sequence counters.

## Dependencies and integration points
It depends on `<linux/const.h>`, `<linux/ioctl.h>`, and `<linux/types.h>`. It integrates with gpiolib, the `/dev/gpiochipN` and anonymous request fds, pinctrl/bias support, hardware timestamping, and libgpiod.

## Risks and test signals
Risks include nonzero reserved padding, duplicate attributes for one line, invalid masks, mixed v1/v2 semantics, event buffer overflow, confusing active with physical polarity, and unsupported bias/drive/timestamp flags. Test signals include libgpiod conformance, ioctl struct-size checks, multi-line get/set ordering, edge-event sequence validation, debounce tests, watch/unwatch events, v1 compatibility tests, and 32/64-bit ABI checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/gpio.h -->
