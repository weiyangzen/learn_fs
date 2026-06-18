# sources/distributed-fs/ceph-client/drivers/phy/st/phy-stih407-usb.c

Purpose: STiH407 USB2 picoPHY provider for per-port USB2 PHY initialization through syscfg and reset controls.

Important APIs, types, and functions: `struct stih407_usb2_picophy` stores PHY, syscfg regmap, global and port resets, and syscfg register offsets. `stih407_usb2_pico_ctrl()` deasserts global reset and writes port control bits. `stih407_usb2_init_port()` writes default PHY parameters and deasserts the port reset. `stih407_usb2_exit_port()` asserts only the port reset.

Control flow: probe gets shared `global` reset and exclusive `port` reset, asserts the port reset by default, parses `st,syscfg` phandle args into parameter/control register offsets, creates one PHY, and registers simple xlate. Init performs global control and port parameter programming before deasserting port reset; exit reasserts port reset.

State and persistence: syscfg offset state is stored in the device object. Hardware state persists in syscfg and reset lines. Global reset is deliberately not asserted on exit because other ports can share it.

Dependencies and integration points: generic PHY, syscon/regmap phandle args, reset controller, STiH407 USB2/USB3 controller consumers.

Risks: `stih407_usb2_pico_ctrl()` return value is ignored in init, so control write errors may be masked until parameter write or reset. Shared global reset policy assumes consumers coordinate via per-port resets and power management.

Test signals: multi-port USB operation, syscfg args validation, reset line observation, init/exit cycles with another port active, and register readback of default parameter value.
