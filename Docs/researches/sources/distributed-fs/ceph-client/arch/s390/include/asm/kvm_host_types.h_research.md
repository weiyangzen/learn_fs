# sources/distributed-fs/ceph-client/arch/s390/include/asm/kvm_host_types.h

Purpose: This header defines packed hardware-facing s390 KVM data structures, especially SCA/ESCA/BSCA blocks and the SIE control block layout.

Important APIs/types/functions: It defines CPU slot counts, SIGP control unions, SCA entries and blocks, IPTE control, utility fields, volatile machine-check save data, CR initial masks, SIDA helpers, CPUSTAT bits, `struct kvm_s390_sie_block`, `struct kvm_s390_itdb`, and `struct sie_page`.

Control flow: KVM allocates and fills these structures before entering SIE. Hardware and low-level assembly read/write fields at fixed offsets for CPU state, intercept reasons, guest PSW, timers, control registers, facilities, crypto control, protected-virtualization handles, and interruption data.

State and persistence: State persists in DMA/aligned pages shared between host KVM code, SIE hardware, and assembly. The `sie_page` combines the SIE block, volatile machine-check data, protected-guest GPR save area, and ITDB with reserved padding.

Dependencies and integration points: It depends on atomic types, s390 page/PSW/control-register definitions, and the architecture Principles of Operation layout for SIE/SCA.

Risks and test signals: Offset, packing, or alignment changes can break guest execution silently. Tests should include compile-time offset checks where available, KVM boot/run, machine-check while guest running, ESCA/BSCA CPU-count limits, protected guests, and migration across facility variants.
