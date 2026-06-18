
# sources/distributed-fs/ceph-client/drivers/hwtracing/intel_th/pti.c

Purpose: Intel TH PTI and LPP output drivers. They program the PTI control register, expose sysfs tuning for port width/free-running clock/clock divider, and optionally choose LPP destination.

Important APIs/types/functions: `struct pti_device` tracks MMIO base, bound TH device, mode, clock settings, pattern generator, and LPP destination state. `pti_width_mode()` maps human-visible widths to register mode codes. `intel_th_pti_activate()` programs `REG_PTI_CTL` then enables GTH tracing. `intel_th_pti_deactivate()` disables GTH tracing and clears the register. Separate `intel_th_driver` objects register names `pti` and `lpp`.

Control flow: probe maps one MMIO resource, allocates state, reads initial hardware config, normalizes default mode/divider, and stores drvdata. Sysfs writes update in-memory state. Activation composes `PTI_CTL` from state and GTH output type, then asks the core/GTH to enable routing.

State and persistence: volatile `pti_device` settings persist while the driver is bound; hardware register state is read at probe and rewritten on activation. No persistent storage.

Dependencies and integration: depends on Intel TH output-driver callbacks, GTH routing through `intel_th_trace_enable/disable()`, and register definitions from `pti.h`.

Risks: `clock_divider_store()` stores the numeric divisor rather than log2 code while show prints `1u << clkdiv`; this should be checked against intended ABI. PTI/LPP share probe/activate code but differ in sysfs attributes and destination bits. No locking protects sysfs updates against activation.

Test signals: register both `pti` and `lpp`, read defaults from hardware, set legal/illegal widths and clock dividers, choose LPP destination only when present, activate/deactivate output, and inspect `REG_PTI_CTL`.
