# sources/distributed-fs/ceph-client/include/xen/interface/hvm/hvm_op.h

Purpose: declares selected HVM operation command numbers and payloads for setting/getting domain parameters, notifying page-table teardown, querying memory type, and configuring x86 event-channel upcall vectors.

Important APIs/types/functions: `HVMOP_set_param`/`HVMOP_get_param` use `struct xen_hvm_param`. `HVMOP_pagetable_dying` uses `struct xen_hvm_pagetable_dying`. `enum hvmmem_type_t` defines `HVMMEM_ram_rw`, `HVMMEM_ram_ro`, and `HVMMEM_mmio_dm`; `HVMOP_get_mem_type` uses `struct xen_hvm_get_mem_type`. On x86, `HVMOP_set_evtchn_upcall_vector` uses `struct xen_hvm_evtchn_upcall_vector`.

Control flow: guests or toolstack components issue HVM hypercalls with these payloads. Parameters are indexed constants from `hvm/params.h`; page-table dying is a hint before destroying top-level page tables; memory type queries classify guest PFNs; x86 vector setup overrides the global callback path for a vCPU.

State and persistence: HVM params and event-channel vectors are domain/vCPU state held by Xen. The header stores none locally.

Dependencies and integration points: includes `xen/interface/xen.h` and is included by `hvm/params.h`. It integrates with HVM/PVH boot, event channels, memory type management, and PV driver page-table lifecycle hints.

Risks: command numbers are ABI. Architecture guards mean non-x86 consumers must not assume vector callback support. `domid` privilege rules are enforced outside this header but must be respected by callers.

Test signals: HVM param set/get round trips, x86 callback vector delivery tests gated by `XENFEAT_hvm_callback_vector`, page-table teardown paths under PV drivers, and memory-type queries for RAM/MMIO pages.
