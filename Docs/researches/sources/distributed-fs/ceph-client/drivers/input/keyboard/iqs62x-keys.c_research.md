## sources/distributed-fs/ceph-client/drivers/input/keyboard/iqs62x-keys.c

Purpose: Azoteq IQS620A/621/622/624/625 key and switch child driver. It maps parent MFD event flags to input keys and hall switches.

Important APIs/types/functions: `struct iqs62x_keys_private` stores the parent core, input device, notifier, switch descriptors, keycode array, max count, and wheel interval cache. `iqs62x_keys_parse_prop()` reads `linux,keycodes` and optional `hall-switch-north/south` child nodes. `iqs62x_keys_init()` unmasks relevant parent event bits and seeds switch state. `iqs62x_keys_notifier()` reports keys/switches and handles reset reinitialization.

Control flow: probe parses firmware data, sets input capabilities, initializes hardware event masks per product family, registers input, then registers with the parent blocking notifier. On parent reset events it re-runs initialization. On normal events it reports all configured key flags and hall switch flags, then emulates wheel key release when interval changes indicate a wheel event.

State/dependencies/integration: state is volatile and tied to the parent `iqs62x_core`, regmap, `iqs62x_events[]`, and blocking notifier chain. Product-specific behavior changes event registers and masks.

Risks and test signals: keycode indices assume alignment with `iqs62x_events`. Wheel events require interval tracking and synthetic release, which is easy to regress. Test each supported product number, hall prox/touch child properties, reset notification, `KEY_RESERVED` masking, notifier unregister, and wheel up/down release generation.
