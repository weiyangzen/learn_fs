# sources/distributed-fs/ceph-client/arch/hexagon/include/asm/hexagon_vm.h

Purpose: Hexagon virtual-machine trap IDs, cache/interrupt ops, and MMU bitfields.

Important APIs/types/functions: functions: `__vmcache_ickill`, `__vmcache_dckill`, `__vmcache_l2kill`, `__vmcache_dccleaninva`, `__vmcache_icinva`, `__vmcache_idsync`, `__vmcache_fetch_cfg`, `__vmintop_nop`, `__vmintop_globen`, `__vmintop_globdis`, `__vmintop_locen`, `__vmintop_locdis`, `__vmintop_affinity`, `__vmintop_get`, `__vmintop_peek`, `__vmintop_status`, `__vmintop_post`, `__vmintop_clear`; types: `VM_CACHE_OPS`, `VM_INT_OPS`; macros: `ASM_HEXAGON_VM_H`, `HVM_TRAP1_VMVERSION`, `HVM_TRAP1_VMRTE`, `HVM_TRAP1_VMSETVEC`, `HVM_TRAP1_VMSETIE`, `HVM_TRAP1_VMGETIE`, `HVM_TRAP1_VMINTOP`, `HVM_TRAP1_VMCLRMAP`, `HVM_TRAP1_VMNEWMAP`, `HVM_TRAP1_FORMERLY_VMWIRE`, `HVM_TRAP1_VMCACHE`, `HVM_TRAP1_VMGETTIME`

Control flow: There is no standalone runtime flow; consumers include the header and expand its constants, inline helpers, types, and prototypes at compile time.

State and persistence: No runtime persistence in this file; it contributes compile-time symbols, declarations, constants, or object selection.

Dependencies and integration: Depends on architecture-local and generic Linux kernel declarations. It integrates with the Hexagon architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: ABI, bitfield, or inline-helper mistakes propagate to many translation units and can break boot, userspace ABI, locking, or memory management.

Test signals: Hexagon cross-build.
