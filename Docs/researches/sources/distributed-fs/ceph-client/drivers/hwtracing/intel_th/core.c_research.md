
# sources/distributed-fs/ceph-client/drivers/hwtracing/intel_th/core.c

Purpose: implements the Intel Trace Hub core bus. It registers the `intel_th` bus, allocates controller instances from PCI/ACPI resources, creates synthetic Trace Hub subdevices, exposes output character devices, and brokers trace activation between output drivers and the GTH switch.

Important APIs/types/functions: `intel_th_driver_register()`/`intel_th_driver_unregister()` wrap Linux driver registration for `struct intel_th_driver`. `intel_th_alloc()` builds an `struct intel_th`, char-device major, IRQ handler, runtime-PM setup, and subdevices. `intel_th_free()` tears that tree down. `intel_th_output_enable()` lets the GTH instantiate output devices discovered from hardware port types. `intel_th_trace_enable()`, `intel_th_trace_switch()`, `intel_th_trace_disable()`, and `intel_th_set_output()` are the cross-driver control API used by MSU/PTI/STH.

Control flow: module init creates debugfs support then registers the bus. Parent controller drivers call `intel_th_alloc()`, which normalizes resources, requests IRQs, and calls `intel_th_populate()`. Population creates GTH and source devices immediately, but defers most output devices until the GTH driver probes and asks for matching output types. Output device sysfs `active` toggles call `intel_th_output_activate()`/`intel_th_output_deactivate()`, which hold module and runtime-PM references, optionally run parent controller activation hooks, prepare the GTH port, then call the output driver's `activate()` or generic GTH enable path.

State and persistence: all state is in kernel memory: IDA controller IDs, `th->thdev[]`, subdevice resource copies, output assignment state, active flags, runtime-PM state, char-device references, and optional host-mode flag. No on-disk persistence exists. Host mode suppresses local output enumeration/configuration.

Dependencies and integration: depends on the Linux device model, bus/driver core, char-device registration, PM runtime, DMA masks, debugfs, IRQ APIs, and Intel TH register/resource definitions from `intel_th.h`. It integrates with parent PCI/ACPI drivers, GTH switch callbacks, output file operations from MSU/PTI-like drivers, and source devices such as STH.

Risks: probe/remove ordering is delicate because outputs are children of the switch and may be dynamically created by GTH probe. Output activation must balance module refs, runtime-PM refs, controller hooks, and trace disable paths. IRQ dispatch assumes output devices with bound drivers; regressions can produce NULL-driver races. Resource rebasing and `.end == 0` whole-BAR semantics are easy to break for new subdevices.

Test signals: boot/probe with representative Intel TH PCI IDs, verify `intel_th` bus devices and `/dev/intel_thN/msc*` nodes, toggle output `active`, exercise MSU reads and STH source routing, unload drivers under open output fds, and test host-mode and no-GTH-driver defer paths.
