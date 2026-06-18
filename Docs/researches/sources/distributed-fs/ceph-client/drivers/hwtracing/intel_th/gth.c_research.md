
# sources/distributed-fs/ceph-client/drivers/hwtracing/intel_th/gth.c

Purpose: implements the Intel TH Global Trace Hub switch driver. It discovers GTH output ports, assigns output devices to ports, configures per-master routing, starts/stops trace capture, and exposes sysfs controls for masters and output-port parameters.

Important APIs/types/functions: `struct gth_device` owns MMIO base, output descriptors, master routing array, dynamic sysfs groups, and `gth_lock`. `struct gth_output` tracks one physical port, its type, bound output descriptor, and masters assigned to it. Core callbacks are `intel_th_gth_probe()`, `assign()`, `unassign()`, `set_output()`, `prepare()`, `enable()`, `trig_switch()`, and `disable()`. Register helpers include `gth_output_set/get()`, `gth_smcfreq_set/get()`, and `gth_master_set()`.

Control flow: probe maps GTH/TSCU/CTS registers. If host mode or debugger scratchpad says the device is externally controlled, it avoids reset and sysfs export. Otherwise it resets GTH, reads each physical port type, asks the Intel TH core to instantiate matching output drivers, then creates `outputs/` and `masters/` sysfs groups. Trace enable programs all assigned masters to the output port, marks the output active, optionally resyncs TSCU, updates scratchpad bits, and asserts store-enable. Disable clears master routing, waits for GTH and output pipeline-empty, clears scratchpad, and stops capture. `trig_switch()` drives CTS to switch MSC multiblock windows.

State and persistence: all state is in memory plus volatile hardware registers: `master[]`, output master bitmaps, bound output pointers, active flags, scratchpad bits, output port config, SWDEST routing, SCR/SCR2 force-store controls, and CTS/TSCU registers.

Dependencies and integration: depends on Intel TH core bus callbacks and register definitions from `gth.h`/`intel_th.h`. It integrates with output drivers through `struct intel_th_output`, with STH through `intel_th_set_output()`, and with sysfs for manual routing.

Risks: GTH reset refuses to run if a debugger is active; callers must honor host mode. Spinlocked sysfs writes can reprogram active routing live. Timeout loops for pipeline empty and CTS trigger only debug-log on timeout, so hardware faults may silently degrade data. `set_output()` has a fixed default port 0 and notes this is not configurable.

Test signals: probe on hardware with multiple port types, inspect `outputs/*_port` and `masters/*`, route a source master to MSC/PTI, toggle output active, exercise MSU multiblock switch, and validate host/debugger-in-use path hides capture configuration.
