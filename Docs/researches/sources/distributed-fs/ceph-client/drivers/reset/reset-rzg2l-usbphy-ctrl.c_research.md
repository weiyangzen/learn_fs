# sources/distributed-fs/ceph-client/drivers/reset/reset-rzg2l-usbphy-ctrl.c

Purpose: Renesas RZ/G2L USB PHY control driver exposing two port resets, keeping the USB PHY PLL/reset register initialized, and creating an auxiliary VBUS regulator platform device.

Important APIs/types/functions: `struct rzg2l_usbphy_ctrl_priv` owns `rcdev`, parent reset, MMIO base, runtime PM, `pwrrdy` syscon field, child `vdev`, and a spinlock. Reset ops update `RESET` bits for port 1/2 and PLL reset. `rzg2l_usbphy_ctrl_pwrrdy_init()` optionally uses the `renesas,sysc-pwrrdy` phandle. PM hooks assert/deassert the parent reset and power-ready state.

Control flow: probe maps MMIO, creates a regmap for `VBENCTL`, enables optional power-ready, deasserts the parent reset, resumes runtime PM, initializes PLL/port resets asserted, registers two reset lines, then registers `rzg2l-usb-vbus-regulator`. Remove and suspend tear down child device, PM, and parent reset in reverse.

State and persistence: reset register bits and optional system-controller power-ready bit hold hardware state. Runtime PM and the child platform device are transient device-managed state.

Dependencies and integration: uses platform MMIO, reset framework, `reset_control`, runtime PM, syscon regmap fields, and Renesas USB PHY/USB VBUS regulator bindings.

Risks and test signals: suspend warns if either PHY reset is deasserted, so consumers must quiesce before suspend. Power-ready phandle masks must be one bit. Test probe error paths, suspend/resume with asserted resets, optional `r9a08g045` power-ready support, and child regulator creation/removal.
