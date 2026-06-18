# sources/distributed-fs/ceph-client/drivers/ptp/ptp_kvm_x86.c

Purpose: supplies the x86 KVM backend for the virtual PTP clock. It uses the `KVM_HC_CLOCK_PAIRING` hypercall to pair host wall time with a guest TSC value, and converts that TSC through pvclock state for precise crosstimestamps.

Important APIs/types/functions: globals `clock_pair_gpa`, `clock_pair_glbl`, and `clock_pair` hold the shared hypercall result page. `kvm_arch_ptp_init()` validates KVM paravirt support, allocates/decrypts a page for encrypted guests, verifies pvclock CPU0 state, and checks the clock-pairing hypercall. `kvm_arch_ptp_exit()` re-encrypts and frees the page for confidential-computing guests. `kvm_arch_ptp_get_clock()` performs a wall-clock pairing and returns seconds/nanoseconds. `kvm_arch_ptp_get_crosststamp()` reads `this_cpu_pvti()`, retries on pvclock version changes, invokes the hypercall, converts `clock_pair->tsc` with `__pvclock_read_cycles()`, and reports `CSID_X86_KVM_CLK`.

Control flow: common init calls x86 init; encrypted guests use a dynamically allocated decrypted page while normal guests use a static global structure. Runtime reads issue `KVM_HC_CLOCK_PAIRING` with `KVM_CLOCK_PAIRING_WALLCLOCK`. Crosstimestamp reads loop until pvclock metadata is stable, so the host-provided TSC and the guest system counter conversion agree.

State and persistence: state is one shared clock-pairing memory area and its guest physical address. It is module-lifetime only. Confidential guest memory state is explicitly restored in exit and in init failure paths.

Dependencies and integration: depends on x86 KVM paravirt, pvclock, `cc_platform_has(CC_ATTR_GUEST_MEM_ENCRYPT)`, `set_memory_decrypted/encrypted()`, KVM UAPI hypercall constants, and the common PTP KVM module.

Risks and test signals: encrypted guest setup is sensitive to cleanup ordering; `clock_pair` must not remain decrypted or leaked on init errors. Crosstimestamp correctness depends on stable pvclock metadata and CPU-local preemption handling in the common layer. Test on non-KVM, KVM without clock pairing, regular KVM, and memory-encrypted guests; verify `PTP_SYS_OFFSET_PRECISE`, rate-limited hypercall error logs, and module unload memory restoration.
