# sources/distributed-fs/ceph-client/arch/arm64/include/asm/rsi_cmds.h
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/rsi_cmds.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/rsi_cmds.h` Implements inline RSI SMC command wrappers for version discovery, realm config, RIPAS state, and attestation token retrieval. It is part of the arm64 Linux architecture layer carried under the distributed filesystem Ceph client source tree, so its effect on Ceph is indirect but foundational: page cache, networking, DMA, scheduling, traps, and memory safety all depend on these architecture contracts being correct.

### Important APIs, Types, And Functions
RSI_GRANULE_SIZE, enum ripas, rsi_request_version(), rsi_get_realm_config(), rsi_ipa_state_get(), rsi_set_addr_range_state(), rsi_attestation_token_init(), rsi_attestation_token_continue(). The file is 162 lines / 3994 bytes, and its exported surface is primarily an include-time ABI for implementation files and generic kernel subsystems.

### Control Flow
Each helper prepares SMCCC registers, issues SMC, and maps returned registers to status/out parameters. Attestation init validates 32-64 byte challenge size and copies the challenge into SMCCC 1.2 registers; continue retrieves token chunks into a granule buffer.

### State, Persistence, And Dependencies
State lives in RMM/realm firmware: ABI version, realm_config contents, RIPAS state, and attestation-in-progress state bound to CPU by the RSI ABI. Depends on arm-smccc, string, memory, rsi_smc; integrates with CCA guest drivers, memory conversion, and attestation flows.

### Integration Points
This header is consumed by arm64 architecture implementation files and generic Linux subsystems rather than by Ceph protocol code directly. It integrates with boot, exception entry, MM, scheduler, KVM, tracing, syscall, signal, CPU feature, or firmware paths as described above, providing the low-level behavior on which higher-level distributed filesystem I/O relies.

### Risks
SMC argument ordering and physical-address alignment are ABI critical; attestation continue must run after init on the same CPU; accepting RSI_REJECT as success would corrupt memory-state assumptions.

### Test Signals
Test against RMM/CCA emulator or hardware for version negotiation, realm config alignment, RIPAS transitions, malformed challenges, and multi-chunk attestation.
