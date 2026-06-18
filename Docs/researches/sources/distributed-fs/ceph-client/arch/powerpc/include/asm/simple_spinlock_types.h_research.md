<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/simple_spinlock_types.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/simple_spinlock_types.h

Purpose: Defines the storage layout for PowerPC simple spinlocks and rwlocks.

Important APIs/types/functions: `arch_spinlock_t`, `arch_rwlock_t`, and unlocked initializers. Source-visible declarations include: #define _ASM_POWERPC_SIMPLE_SPINLOCK_TYPES_H; typedef struct {; #define __ARCH_SPIN_LOCK_UNLOCKED { 0 }; typedef struct {; #define __ARCH_RW_LOCK_UNLOCKED { 0 }.

Control flow: included before primitive implementations and by lockdep/generic lock code. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: lock values persist in the object embedding these types. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are no direct includes. Integrated with simple spinlock backend selected when queued locks are disabled.

Risks: type layout is ABI for assembly/inlines and must match lock algorithms. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 21 lines, 487 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/simple_spinlock_types.h -->
