# sources/distributed-fs/ceph-client/arch/mips/include/asm/mmzone.h

Purpose: MIPS memory-zone/NUMA include shim and fallback physical-address-to-node helpers.

Important APIs/types/functions: Includes `asm/page.h`; under `CONFIG_NUMA`, includes `<mmzone.h>`. Provides fallback `pa_to_nid(addr) 0` and `nid_to_addrbase(nid) 0` when not defined elsewhere.

Control flow, state, and persistence: No runtime behavior. The macros make non-NUMA builds report all physical memory as node 0.

Dependencies and integration: Integrated with generic memory-management code that expects `pa_to_nid` and `nid_to_addrbase`. NUMA platforms can override them through included headers.

Risks and test signals: Fallbacks are correct only for non-NUMA or UMA platforms. Test NUMA builds for real overrides, non-NUMA builds for successful memory init, and memory hotplug or node lookup paths.
