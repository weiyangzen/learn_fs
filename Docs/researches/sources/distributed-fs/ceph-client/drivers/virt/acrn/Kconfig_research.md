# sources/distributed-fs/ceph-client/drivers/virt/acrn/Kconfig

Purpose: Kconfig entry for the ACRN Hypervisor Service Module. It controls the `/dev/acrn_hsm` management driver used in ACRN Service VMs.

Important APIs, types, and functions: config symbol `ACRN_HSM` is tristate, depends on `ACRN_GUEST`, and selects `EVENTFD`.

Control flow: enabling this config builds the ACRN HSM module or built-in driver; the help text documents that it is for privileged management Service VMs, not ordinary User VMs.

State and persistence: build configuration state only.

Dependencies and integration points: consumed by `drivers/virt/Makefile` and `drivers/virt/acrn/Makefile`; runtime code checks ACRN hypervisor and privileged-VM CPUID feature before registering.

Risks: selecting it in a non-privileged ACRN guest compiles but runtime init returns permission/state errors. Eventfd is required for ioeventfd/irqfd integration.

Test signals: Kconfig dependency resolution with and without `ACRN_GUEST`; built-in and module builds; runtime registration only in privileged Service VM.
