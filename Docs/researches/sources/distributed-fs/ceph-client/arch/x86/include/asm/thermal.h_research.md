<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/thermal.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/thermal.h

Purpose: declares x86 thermal interrupt/vector initialization hooks. Important APIs are `therm_lvt_init()`, `intel_init_thermal()`, `x86_thermal_enabled()`, and `intel_thermal_interrupt()` when `CONFIG_X86_THERMAL_VECTOR` is enabled, with stubs otherwise.

Control flow: CPU initialization sets up local APIC thermal vector handling and Intel CPU thermal support; interrupts dispatch to the thermal handler. State is CPU thermal/APIC configuration owned by implementation. Dependencies include CPU detection, APIC LVT thermal vector, and thermal/interrupt subsystems.

Risks include missing thermal interrupts, false enablement on unsupported CPUs, and build issues for stubbed `x86_thermal_enabled()` users. Test signals include thermal vector initialization, simulated thermal interrupts, CPU hotplug, and no-thermal-vector builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/thermal.h -->
