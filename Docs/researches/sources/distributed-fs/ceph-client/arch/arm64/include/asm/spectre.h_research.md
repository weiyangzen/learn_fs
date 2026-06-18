# sources/distributed-fs/ceph-client/arch/arm64/include/asm/spectre.h
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/spectre.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/spectre.h` Declares arm64 Spectre/Meltdown mitigation state, branch predictor hardening hooks, hyp vector slot choices, and alternative patch callbacks. It is part of the arm64 Linux architecture layer carried under the distributed filesystem Ceph client source tree, so its effect on Ceph is indirect but foundational: page cache, networking, DMA, scheduling, traps, and memory safety all depend on these architecture contracts being correct.

### Important APIs, Types, And Functions
enum mitigation_state, enum arm64_hyp_spectre_vector, bp_hardening_cb_t, struct bp_hardening_data, per-CPU bp_hardening_data, arm64_apply_bp_hardening(), arm64_get_spectre_*_state(), has_spectre_*(), spectre_*_enable_mitigation(), spectre_v4_enable_task_mitigation(), BHB patch callbacks, try_emulate_el1_ssbs(), spectre_print_disabled_mitigations(). The file is 123 lines / 3890 bytes, and its exported surface is primarily an include-time ABI for implementation files and generic kernel subsystems.

### Control Flow
Entry code calls arm64_apply_bp_hardening; if ARM64_SPECTRE_V2 alternative cap is present, it fetches per-CPU hardening data and invokes the callback. Other functions are implemented elsewhere to detect CPU vulnerability and patch mitigation sequences.

### State, Persistence, And Dependencies
Persistent state is per-CPU bp_hardening_data and alternative/static CPU capability state; per-task SSBS mitigation state is managed through task flags. Depends on smp, percpu, cpufeature, virt; integrates exception entry, KVM hyp vectors, SMCCC firmware workarounds, alternatives, scheduler task mitigation, and sysfs vulnerability reporting.

### Integration Points
This header is consumed by arm64 architecture implementation files and generic Linux subsystems rather than by Ceph protocol code directly. It integrates with boot, exception entry, MM, scheduler, KVM, tracing, syscall, signal, CPU feature, or firmware paths as described above, providing the low-level behavior on which higher-level distributed filesystem I/O relies.

### Risks
Mitigation ordering and vector-slot enum order are security critical; missing callbacks or wrong patching can leave speculation vulnerabilities exposed or crash exception entry.

### Test Signals
Run spectre selftests, CPU capability matrix boots, KVM hyp vector tests, SMCCC conduit tests, sysfs vulnerability checks, and alternative patch validation.
