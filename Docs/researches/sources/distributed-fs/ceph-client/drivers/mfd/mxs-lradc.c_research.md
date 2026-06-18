# sources/distributed-fs/ceph-client/drivers/mfd/mxs-lradc.c

Purpose: MFD splitter for Freescale i.MX23/i.MX28 LRADC hardware. It claims the parent clock and memory resource, chooses SoC-specific ADC/touchscreen child resources, parses touchscreen wiring, and registers ADC plus optional touchscreen children.

Important APIs, types, and functions: SoC-specific IRQ enums and resource arrays define ADC and touchscreen resource sets. `mxs_lradc_dt_ids[]` maps compatibles to `IMX23_LRADC` or `IMX28_LRADC`. `mxs_lradc_probe()` allocates `struct mxs_lradc`, enables the clock, parses `fsl,lradc-touchscreen-wires`, copies the parent MEM resource into child resource slot 0, and uses `devm_mfd_add_devices()` for `mxs-lradc-adc` and optional `mxs-lradc-ts`. `mxs_lradc_remove()` disables the clock.

Control flow: probe must enable the delay-unit clock before children can use hardware. If touchscreen wiring is absent, all buffer virtual channels are available to the ADC child and only ADC is registered. If wiring is present, limited buffer channels and touchscreen mode are configured, then both ADC and touchscreen children are added.

State and persistence: parent state holds SoC type, clock, touchscreen wire mode, and buffer channel policy. Static resource arrays are mutated with the probed MEM resource, so they become instance-specific.

Dependencies and integration points: depends on platform resources, OF properties, clk API, MFD core, and public `<linux/mfd/mxs-lradc.h>`. Child drivers rely on the shared memory region and IRQ resources.

Risks: static mutable resource arrays make multiple LRADC instances unsafe. If touchscreen child registration fails after ADC registration, devm cleanup later removes ADC but the probe manually only disables the clock. Unsupported 5-wire mode on i.MX23 is rejected. Test signals include i.MX23/i.MX28 resource mapping, touchscreen property validation, clock enable/disable on all failure paths, ADC-only mode, and child resource IRQ names.
