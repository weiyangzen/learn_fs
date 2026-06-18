# sources/distributed-fs/ceph-client/drivers/input/rmi4/rmi_f21.c

## Purpose

`rmi_f21.c` implements RMI4 Function 21 for force-click/buttonpad reporting. It reports a single force-click button as `BTN_LEFT` and marks the shared input device as a buttonpad.

## Important APIs, Types, and Functions

`struct f21_data` stores the shared input device, keycode, attention/data packet sizes and offsets, and a data buffer. `rmi_f21_initialize()` configures the input key table and `INPUT_PROP_BUTTONPAD`. `rmi_f21_probe()` derives packet sizing from function query bits. `rmi_f21_attention()` reads or consumes the button byte and reports the key.

## Control Flow

Probe requires an existing shared input device, allocates state, initializes key capabilities, then computes attention and register-read sizes from sensor count, finger-count-present, and new-report-format query bits. Config always enables the function IRQ. On attention, the handler uses transport attention data when present and advances the shared pointer, otherwise reads the full data register block. It extracts the force-click bit from the computed button offset and reports `BTN_LEFT`.

## State and Persistence Behavior

State is limited to query-derived offsets/sizes and the keycode stored in the input device. Hardware state is not modified except IRQ mask enablement. The data buffer is reused for direct register reads.

## Dependencies and Integration Points

The file integrates with RMI core reads, shared transport attention data, RMI IRQ masks, and Linux input key reporting. It also relies on the RMI core having already created `drv_data->input`.

## Risks and Edge Cases

The code tests feature bits against `fn->fd.query_base_addr` rather than a byte read from the query register, which is unusual and likely fragile unless the function descriptor has been repurposed by this source variant. Packet-size math depends on sensor and finger counts staying within fixed maxima. Attention data shorter than the computed size is ignored after a warning. No explicit `input_sync()` is issued.

## Test Signals

Useful checks include old and new report formats, devices with and without finger-count query data, transport attention and direct-read paths, press/release reporting, buttonpad property visibility, and fault injection for missing input devices or truncated attention data.
