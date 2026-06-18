# sources/distributed-fs/ceph-client/drivers/input/joystick/adc-joystick.c

Purpose: Platform input driver for joysticks wired to IIO ADC channels. It supports either input-core polling via `iio_read_channel_raw()` or callback-buffer driven reporting from IIO scan data, with axis layout supplied by firmware child nodes.

Important APIs/types/functions: `struct adc_joystick` owns the input device, IIO channel list, optional IIO callback buffer, and flexible-array axis metadata. `struct adc_joystick_axis` stores an input ABS code and inversion flag. `adc_joystick_probe()` acquires all IIO channels, reads the optional `poll-interval`, allocates the variable-sized state object, configures axes, chooses polling or callback mode, and registers the input device. `adc_joystick_set_axes()` consumes child-node `reg`, `linux,code`, `abs-range`, `abs-fuzz`, and `abs-flat`. `adc_joystick_handle()` decodes scan buffers using channel `scan_index`, endian, shift, sign, storagebits, and realbits; `adc_joystick_poll()` performs raw channel reads.

Control flow: Probe requires a one-to-one match between child nodes and IIO channels. In polling mode, input polling reads each channel and reports configured ABS codes. In buffered mode, input open starts the IIO callback buffer and close stops it; the callback decodes all samples and calls `input_sync()`.

State and persistence: Runtime state is per device and devm/action managed. No persistent storage exists. Axis inversion is derived once from a reversed `abs-range` and then applied to every sample.

Dependencies and integration points: Integrates with platform bus, device properties/OF compatible `adc-joystick`, IIO consumer APIs, and the input polling/callback model. Buffered operation depends on channels having equal storage size and storagebits no larger than 16.

Risks: Firmware must provide correct child-node ordering and ranges; invalid or mismatched nodes fail probe. Buffered decode assumes all channels share storage size and only supports 8- or 16-bit storage. Inversion calls `adc_joystick_invert()` with loop index in the current tree, while ABS min/max are configured by ABS code, so non-contiguous ABS codes deserve review in tests.

Test signals: Probe with valid and invalid child-node counts; poll mode with `poll-interval`; callback mode with BE, LE, CPU endian and signed/unsigned scan types; reversed `abs-range`; open/close start-stop of IIO buffers; input event ranges matching DT-specified ABS codes.
