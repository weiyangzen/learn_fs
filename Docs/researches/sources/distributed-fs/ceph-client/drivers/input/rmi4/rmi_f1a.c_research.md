# sources/distributed-fs/ceph-client/drivers/input/rmi4/rmi_f1a.c

## Purpose

`rmi_f1a.c` implements RMI4 Function 1A for simple capacitive button reporting. It maps a firmware-provided button bitmask to Linux input key events using keycodes supplied through the `linux,keycodes` device property.

## Important APIs, Types, and Functions

`struct f1a_data` stores the shared input device, keymap pointer, and key count. `rmi_f1a_parse_device_properties()` reads the `linux,keycodes` property. `rmi_f1a_initialize()` registers key capabilities and installs the input keycode table. `rmi_f1a_attention()` reads the F1A data bitmask and reports each key. `rmi_f1a_config()` enables the function IRQ only when keys are configured.

## Control Flow

Probe requires the RMI core-created input device, allocates `f1a_data`, parses optional keycodes, initializes input capabilities, and stores driver data. Config sets the function IRQ mask if at least one key was configured. Attention reads one byte from the function data base address and emits `input_report_key()` for each configured key.

## State and Persistence Behavior

The keymap is devm-managed and attached to the shared input device as `input->keycode`. No hardware state is changed besides IRQ enablement. Button state is sampled on attention and not stored in the function data structure.

## Dependencies and Integration Points

The file depends on the Linux device-property API, input core, RMI reads, RMI IRQ mask management, and the shared input device in `rmi_driver_data`.

## Risks and Edge Cases

Only one byte of button state is read, so more than eight configured keycodes would not be represented correctly. If the keycode property is absent, probe succeeds with zero keys and config leaves IRQs disabled. The attention path does not call `input_sync()`, relying on surrounding RMI/input flow to sync or tolerate batched reports.

## Test Signals

Tests should cover valid, missing, empty, and malformed `linux,keycodes`; one to eight button maps; too-many key maps; IRQ enablement when `num_keys` is zero; and key press/release reporting from data-register bit changes.
