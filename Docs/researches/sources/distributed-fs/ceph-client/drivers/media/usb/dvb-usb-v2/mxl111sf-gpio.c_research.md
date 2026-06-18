# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/mxl111sf-gpio.c

Purpose: GPIO, port-expander, and pin-mux helper implementation for MxL111SF-based Hauppauge devices. It abstracts internal MxL111SF GPIO registers and optional PCA9534-like I2C expanders, then uses them to switch between DVB-T, ATSC, and mobile-DTV board modes.

Important APIs/types/functions: internal helpers `mxl111sf_set_gpo_state()`, `mxl111sf_get_gpi_state()`, and `mxl111sf_config_gpio_pins()` operate on hardware pins. `mxl111sf_config_pin_mux_modes()` rewrites mux/control registers for TS output, GPIO, serial/parallel TS input, SPI input, and BT656/I2S modes. `mxl111sf_set_gpio()`, `mxl111sf_init_port_expander()`, and `mxl111sf_gpio_mode_switch()` are the exported driver helpers. PCA9534 paths use `i2c_transfer()` on the device adapter.

Control flow: board attach and frontend init call `mxl111sf_init_port_expander()` to detect and initialize external GPIO hardware or fall back to internal GPIO. For ATSC/MH profiles, `mxl111sf_gpio_mode_switch()` powers/reset-lines the LG demodulators in a timed sequence and selects transport mode with GPIO3. Pin mux programming is selected by profile and streaming path, especially SPI versus transport-stream input on v8 silicon.

State and persistence: persistent state lives in `mxl111sf_state`: `gpio_port_expander`, `port_expander_addr`, and current `gpio_mode`. Hardware-visible persistence is in MxL111SF mux/GPO registers and the port-expander output/config registers. There is no cleanup path restoring default GPIO levels beyond mode switches.

Dependencies and integration: depends on MxL111SF register helpers, I2C adapter access, and the main board driver's frontend mode decisions. The helper is tightly integrated with Hauppauge board wiring: GPIO3-7 are interpreted as ATSC/MH reset, enable, and transport selectors.

Risks: `pca9534_set_gpio()` and `pca9534_init_port_expander()` ignore `i2c_transfer()` return values and always report success. `pca9534_set_gpio()` uses fixed `PCA9534_I2C_ADDR`, not `state->port_expander_addr`, despite probing two possible addresses. Large mux updates are written register by register without rollback, so partial failures can leave mixed pin modes. Several helper calls in mode switching ignore errors.

Test signals: attach boards with and without a port expander; verify probe at 0x70/0x40 and hardware GPIO fallback; switch DVB-T, ATSC, and MH modes repeatedly; check GPIO line levels with hardware instrumentation; test SPI/isoc/bulk profiles on v6 and v8 chips; confirm errors propagate from internal GPIO register access.
