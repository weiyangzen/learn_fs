# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/ti-tdp158.c

Purpose: provides a small DRM bridge driver for the TI TDP158 HDMI/DVI retimer/redriver. It models the chip as an I2C device that powers two regulators and an optional operation-enable GPIO around bridge enable/disable, then passes attach through to the next bridge.

Important APIs/types/functions: `struct tdp158` stores the embedded `drm_bridge`, downstream bridge, enable GPIO, `vcc` and `vdd` regulators, and device pointer. `tdp158_probe()` allocates the bridge with `devm_drm_bridge_alloc()`, gets the downstream bridge from OF graph port 1, obtains `vcc` and `vdd` regulators, gets optional `enable` GPIO initialized low, fills `bridge.of_node` and `driver_private`, and registers with `devm_drm_bridge_add()`. `tdp158_attach()` delegates to `drm_bridge_attach()`. `tdp158_enable()` enables `vcc`, enables `vdd`, and asserts enable; `tdp158_disable()` deasserts enable and disables regulators in reverse order.

Control flow: the bridge has no mode validation, format negotiation, HPD, EDID, or runtime PM. It relies on its position in the bridge chain and the downstream bridge for connector behavior. Atomic enable/disable are the only runtime hooks.

State and persistence: there is no explicit software state beyond devm-managed pointers. Hardware state is the regulator and enable GPIO levels. Failed regulator enables are logged but do not abort the enable callback or roll back the other rail.

Dependencies and integration points: depends on DRM bridge atomic helper state allocation, OF graph bridge lookup, regulator framework, GPIO consumer API, and I2C driver matching via `ti,tdp158`. It integrates into display pipelines as a transparent bridge that must be powered when the upstream encoder drives TMDS.

Risks: ignored regulator errors can leave the enable GPIO asserted with one rail missing. Disable unconditionally calls `regulator_disable()` even if enable failed partially. No timing delays are implemented around regulator and enable sequencing, so board-specific requirements must be satisfied externally or by regulator/GPIO constraints.

Test signals: device-tree graph probe/defer, regulator failure injection, enable/disable sequencing on suspend and modeset, bridge-chain attach with downstream bridge, and checking that the optional enable GPIO being absent is tolerated.
