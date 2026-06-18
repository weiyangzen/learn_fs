## `sources/distributed-fs/ceph-client/arch/x86/hyperv/hv_vtl.c`

Purpose: supports Linux running in a non-default Hyper-V Virtual Trust Level, especially VTL2. It disables firmware assumptions, implements AP bring-up through Hyper-V VTL hypercalls, and provides VTL return-call support.

Important APIs and functions: `hv_vtl_init_platform()` rewrites x86 platform hooks for VTL mode; `hv_vtl_early_init()` installs restart and AP wakeup overrides; `hv_vtl_wakeup_secondary_cpu()` maps APIC ID to VP index; `hv_vtl_bringup_vcpu()` builds 64-bit CPU context and issues `HVCALL_ENABLE_VP_VTL`/`HVCALL_START_VP`; `mshv_vtl_return_call_init()` and `mshv_vtl_return_call()` wrap the VTL return hypercall.

Control flow: early init rejects XSAVE, installs a dummy real-mode header, and patches AP startup. Platform init disables BIOS/real-mode/legacy device paths and uses triple fault for restart. AP bring-up obtains idle stack and current GDT/IDT/TSS/LDT state, fills the Hyper-V VP context with long-mode descriptors/control registers, enables the target VTL, and starts the VP at `hv_vtl_ap_entry()`.

State and persistence: stores VTL state in `ms_hyperv.vtl`, a static real-mode header, and a static call for VTL return. `mshv_vtl_return_call()` temporarily uses VP assist return registers and FPU save/restore around the transition.

Dependencies and integration points: Hyper-V hypercalls, APIC callback replacement, x86 platform init hooks, GDT/IDT/TSS descriptors, FPU state management, and `mshv_vtl_asm.S`.

Risks: AP context values are architectural and exact; wrong descriptors or control registers prevent secondary CPU startup. XSAVE is explicitly unsupported. FPU handling and VTL transition assembly must remain noinstr-safe.

Test signals: VTL2 boot, secondary CPU bring-up, restart via triple fault, VTL return hypercall round trips, and boot failure when XSAVE is not disabled.
