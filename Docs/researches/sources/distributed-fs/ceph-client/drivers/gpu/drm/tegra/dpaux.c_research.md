# sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/dpaux.c

## Purpose
`dpaux.c` implements the Tegra DisplayPort AUX controller platform driver and exposes it as a DRM `struct drm_dp_aux`. It handles AUX and I2C-over-AUX transactions, HPD plug/unplug IRQs, AUX bus population, optional panel power polling, pad muxing between AUX/I2C/off modes, runtime PM, clock/reset/regulator sequencing, and global lookup by device tree node.

## Important APIs, Types, and Functions
`struct tegra_dpaux` embeds `struct drm_dp_aux`, the device/register/IRQ handles, output attachment, reset and clock handles, optional regulator, transaction completion, hotplug work item, global list entry, and optional pinctrl state. `struct tegra_dpaux_soc` stores pad drive calibration constants.

The public helpers declared in `drm.h` are `drm_dp_aux_find_by_of_node()`, `drm_dp_aux_attach()`, `drm_dp_aux_detach()`, `drm_dp_aux_detect()`, `drm_dp_aux_enable()`, and `drm_dp_aux_disable()`. Core transport is `tegra_dpaux_transfer()`, installed as `aux.transfer`. IRQ and hotplug handling are in `tegra_dpaux_irq()` and `tegra_dpaux_hotplug()`.

## Control Flow
Probe allocates the controller, stores SoC data, initializes work/completion/list state, maps registers, gets IRQ/reset/clocks/regulator, sets the parent clock rate to 270 MHz, enables runtime PM and takes an initial PM reference, requests and disables the IRQ, initializes the DRM AUX object, configures pads to I2C mode for HDMI by default, optionally registers pinctrl, enables/clears AUX interrupts, adds the object to a global mutex-protected list, and populates DP AUX bus endpoint devices.

Each AUX transfer validates the 16-byte FIFO limit, encodes zero-length I2C address-only transactions when allowed, maps DRM AUX requests to Tegra command bits, writes address/control and optional write FIFO data, sets `TRANSACTREQ`, waits for completion signaled by IRQ, reads and clears status, maps hardware timeout/RX/sink/no-stop errors to Linux errors, translates hardware reply type to DRM AUX reply codes, and reads back FIFO data for successful reads with exact-length validation.

Attach registers the AUX channel with DRM, stores the output, enables HPD polling, optionally enables panel VDD, polls HPD connected for up to 250 ms, then enables IRQ. Detach unregisters AUX, disables IRQ, optionally disables panel VDD and polls for disconnect, then clears output for panel-backed paths. Runtime suspend asserts reset and disables clocks; resume enables clocks and deasserts reset.

## State and Persistence
Persistent in-memory state includes the global `dpaux_list`, each `tegra_dpaux` object, its output pointer, completion object, work item, pinctrl device, and regulator/clock/reset handles. Hardware state includes pad mode/power, interrupt enable/status, AUX transaction registers, and HPD status. There is no disk persistence.

## Dependencies and Integration Points
The file integrates with DRM DP helper APIs, DRM AUX bus population, DRM panel and HPD helpers, Tegra tracepoints, Linux platform/PM/clock/reset/regulator subsystems, pinctrl/pinmux when enabled, and output drivers that find a DPAUX node and attach a `tegra_output`.

## Risks
The transfer path depends on IRQ completion and can timeout if IRQs are disabled or status bits are missed. Read response length mismatch is converted to `-EBUSY` to trigger helper retries, which is intentional but can hide hardware quirks. `drm_dp_aux_attach()` returns early on regulator/panel polling failures after AUX registration or regulator enable without fully unwinding all intermediate state. `drm_dp_aux_detach()` clears `output` only in the panel path, so non-panel detach keeps a stale pointer until reattach/remove. Pad mux defaults to I2C for HDMI, so DP paths must call enable/disable at the right time.

## Test Signals
Useful validation includes AUX native reads of DPCD, I2C-over-AUX EDID reads, retry behavior under short replies, HPD plug/unplug IRQ work firing `drm_helper_hpd_irq_event()`, panel-backed attach/disconnect polling, runtime suspend/resume preserving transaction ability, pinctrl mode changes for `aux`, `i2c`, and `off`, and trace logs showing expected AUX register writes/status clears.
