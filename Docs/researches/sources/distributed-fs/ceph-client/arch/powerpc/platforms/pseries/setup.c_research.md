# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/setup.c

Purpose: Main pSeries platform setup file: machine probing, early architecture initialization, interrupt/controller setup, PCI discovery, FWNMI setup, LPAR idle/accounting, security mitigations, CMO parsing, power-off, and machine descriptor registration.

Important APIs/types/functions: Defines globals such as `shared_processor`, CMO values, `fwnmi_active`, `ibm_nmi_interlock_token`, and `pseries_security_flavor`. Key functions include `fwnmi_init()`, `pseries_init_irq()`, DTL allocation, LPAR idle, relocation-on-exception controls, PCI PHB discovery and SR-IOV fixups, `pseries_setup_security_mitigations()`, `pSeries_setup_arch()`, `pseries_init()`, `pseries_power_off()`, `pSeries_probe()`, and `define_machine(pseries)`.

Control flow: Probe validates CHRP/pSeries compatibility, installs power-off, and runs early pseries init. Setup initializes SMP/hotplug, FWNMI buffers, security mitigations, PCI flags/tokens/notifiers, NVRAM, VPA/shared-processor behavior, idle/PMC hooks, SR-IOV hooks, root bridge prepare, and RNG. The machine descriptor wires RTAS and RAS handlers into generic powerpc callbacks.

State and persistence: Maintains machine-wide feature globals, CMO parameters from sysparm, FWNMI per-CPU buffer pointers, DTL cache, relocation-on-exception state, and machine descriptor hooks.

Dependencies and integration points: Integrates almost every pSeries subsystem: RTAS, hcalls, OF, PCI/MSI/IOMMU, XICS/XIVE, VPA/DTL, security feature framework, fadump/RAS, CMO, RNG, kexec, PM, NVRAM, and powerpc machine descriptors.

Risks: Init ordering is critical because callbacks are installed before later subsystems use them. FWNMI buffers must be below RMA. Security mitigation defaults must be reset before migration-sensitive hcall updates. CMO string parsing mutates a sysparm buffer and must stay within firmware length bounds. Power-off intentionally never returns.

Test signals: Boot on LPAR and non-LPAR pSeries, radix/hash MMU, XIVE/XICS fallback, FWNMI MCE/system reset, migration security-feature refresh, SR-IOV firmware BAR parsing, CMO sysparm parsing, shared processor accounting, kexec/kdump endian exception paths, and power-off UPS flag behavior.

Source read size: 1165 lines, 33429 bytes.
