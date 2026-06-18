# sources/distributed-fs/ceph-client/drivers/usb/cdns3/cdns3-ti.c

Purpose: Provides the TI K3/AM64/J721E wrapper for Cadence USB3, configuring wrapper reset, reference clock rate encoding, optional USB2-only and VBUS divider properties, child device population, runtime PM, and a DRD suspend residency quirk.

Important APIs, types, and functions: `struct cdns_ti` stores wrapper MMIO, property flags, `ref` and `lpm` clocks, and encoded reference clock rate. `cdns_ti_rate_table` maps supported kHz rates to hardware codes. `cdns_ti_reset_and_init_hw` asserts reset, programs static config, USB2-only mode, and modestrap, then deasserts reset. Probe obtains resources/clocks/properties, validates refclk rate, initializes hardware, enables runtime PM, and populates `cdns,usb3` children with platform data. Runtime resume reinitializes hardware if reset bits indicate uninitialized state.

Control flow: Probe performs a manual reset before the first `pm_runtime_get_sync` so runtime resume observes initialized hardware. Child devices are unregistered on remove before runtime PM is released. Runtime resume is idempotent by checking `USBSS_W1_PWRUP_RST | USBSS_W1_MODESTRAP_SEL`.

State and persistence behavior: State is in `struct cdns_ti`, wrapper registers, clock state, and runtime PM reference. No persistent storage. Wrapper state may be lost across runtime/system suspend and is repaired on resume.

Dependencies and integration points: Uses platform MMIO, clock APIs, OF platform population, device properties `ti,vbus-divider` and `ti,usb2-only`, runtime PM, and `cdns3_platform_data` quirks. Compatible strings are `ti,j721e-usb` and `ti,am64-usb`.

Risks: Unsupported refclk rates fail probe. The rate table order is hardware ABI; changing it changes register programming. Error path after child population failure must balance runtime PM. Runtime resume only checks two wrapper bits, so partially corrupted static config may not be repaired. `lpm_clk` is obtained but not explicitly enabled in this file, relying on runtime/core behavior.

Test signals: Supported and unsupported reference clocks, `ti,vbus-divider`, `ti,usb2-only`, child populate failure, runtime resume after wrapper reset, system sleep through `pm_runtime_force_suspend/resume`, and host/gadget operation on J721E/AM64.
