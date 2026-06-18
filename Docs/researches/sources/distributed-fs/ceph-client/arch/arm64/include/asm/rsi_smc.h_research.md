# sources/distributed-fs/ceph-client/arch/arm64/include/asm/rsi_smc.h
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/rsi_smc.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/rsi_smc.h` Defines the Arm CCA RSI SMC ABI constants, statuses, feature IDs, realm_config layout, RIPAS flags, and host-call function IDs. It is part of the arm64 Linux architecture layer carried under the distributed filesystem Ceph client source tree, so its effect on Ceph is indirect but foundational: page cache, networking, DMA, scheduling, traps, and memory safety all depend on these architecture contracts being correct.

### Important APIs, Types, And Functions
RSI_ABI_VERSION*, RSI_SUCCESS/error constants, SMC_RSI_FID(), SMC_RSI_* function IDs, struct realm_config aligned to 4K, RSI_NO_CHANGE_DESTROYED, RSI_CHANGE_DESTROYED, RSI_ACCEPT, RSI_REJECT. The file is 193 lines / 5357 bytes, and its exported surface is primarily an include-time ABI for implementation files and generic kernel subsystems.

### Control Flow
No runtime flow in the header; it encodes the ABI consumed by rsi_cmds.h and assembly/C callers.

### State, Persistence, And Dependencies
Persistent ABI state is in firmware and shared buffers such as realm_config. Header owns no runtime state. Depends on linux/arm-smccc.h; integrates with Realm Management Monitor services, CCA memory state, attestation, measurements, and host calls.

### Integration Points
This header is consumed by arm64 architecture implementation files and generic Linux subsystems rather than by Ceph protocol code directly. It integrates with boot, exception entry, MM, scheduler, KVM, tracing, syscall, signal, CPU feature, or firmware paths as described above, providing the low-level behavior on which higher-level distributed filesystem I/O relies.

### Risks
Any numeric FID/status/layout change breaks firmware ABI; realm_config alignment and padding must remain exactly as required by RMM.

### Test Signals
Validate with ABI conformance tests, static layout assertions, RMM emulator smoke tests, and endian/packing checks.
