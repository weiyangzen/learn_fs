# sources/distributed-fs/ceph-client/arch/arm64/include/asm/rsi.h
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/rsi.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/rsi.h` Defines top-level Arm CCA Realm Services Interface presence and memory-state helpers. It is part of the arm64 Linux architecture layer carried under the distributed filesystem Ceph client source tree, so its effect on Ceph is indirect but foundational: page cache, networking, DMA, scheduling, traps, and memory safety all depend on these architecture contracts being correct.

### Important APIs, Types, And Functions
RSI_PDEV_NAME, static key rsi_present, arm64_rsi_init(), arm64_rsi_is_protected(), is_realm_world(), rsi_set_memory_range(), rsi_set_memory_range_protected(), rsi_set_memory_range_protected_safe(), rsi_set_memory_range_shared(). The file is 70 lines / 1677 bytes, and its exported surface is primarily an include-time ABI for implementation files and generic kernel subsystems.

### Control Flow
rsi_set_memory_range loops until the requested physical range reaches end, invoking rsi_set_addr_range_state and validating returned top progression; wrappers select RAM/EMPTY and destroyed-page policy.

### State, Persistence, And Dependencies
Persistent state is the rsi_present static key and RMM-owned RIPAS state for IPA ranges. Header owns no storage beyond declarations. Depends on errno, jump_label, rsi_cmds; integrates with Arm CCA realm boot, mem-encryption/shared-memory handling, pgtable-prot PROT_NS_SHARED, and device exposure.

### Integration Points
This header is consumed by arm64 architecture implementation files and generic Linux subsystems rather than by Ceph protocol code directly. It integrates with boot, exception entry, MM, scheduler, KVM, tracing, syscall, signal, CPU feature, or firmware paths as described above, providing the low-level behavior on which higher-level distributed filesystem I/O relies.

### Risks
Bad range progression handling could loop or accept partial conversions; wrong destroyed-page flags can lose data or share protected memory incorrectly.

### Test Signals
Run CCA realm boot, shared/protected memory conversion tests, invalid range tests, and non-realm static-key false-path builds.
