# sources/distributed-fs/ceph-client/arch/x86/include/asm/virt.h

Purpose: Declares x86 virtualization lifetime and emergency-disable coordination APIs used by KVM and reboot/panic paths.

Important APIs/types/functions: `cpu_emergency_virt_cb` is a per-CPU emergency callback type. With `CONFIG_KVM_X86`, `virt_rebooting`, `x86_virt_init()`, `x86_virt_get_ref(int feat)`, `x86_virt_put_ref(int feat)`, `x86_virt_emergency_disable_virtualization_cpu()`, and callback register/unregister functions are declared. Without KVM, init is a no-op and emergency disable returns `-ENOENT`.

Control flow: Architecture init calls `x86_virt_init()`. Virtualization users take/release feature refs. Reboot or emergency paths can disable CPU virtualization and invoke registered callbacks.

State and persistence: Runtime state is external: refcounts, callback lists, and `virt_rebooting`. This header only exposes the API.

Dependencies and integration points: Includes `asm/reboot.h` and is tied to KVM x86, CPU virtualization enable/disable code, and emergency reboot/shutdown paths.

Risks: Refcount bugs can leave VMX/SVM enabled during emergency paths or disable it while still in use. Callback registration must be synchronized in implementation. Stubs must preserve callers' ability to build without KVM.

Test signals: KVM module load/unload, reboot and panic tests while VMs run, nested virtualization toggles, and non-KVM build coverage.
