
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/mce_power.c

Purpose: POWER7/8/9/10 CPU-side real-mode machine-check decoder and recovery logic, translating SRR1/DSISR signatures into structured MCE information and attempting SLB/ERAT/TLB recovery or UE fixups.

Important APIs/types/functions: `addr_to_pfn`; `flush_and_reload_slb`; `flush_erat`; `mce_flush`; P7/P8/P9/P10 instruction and data error tables; `mce_handle_ierror`; `mce_handle_derror`; `mce_find_instr_ea_and_phys`; `mce_handle_ue_error`; `mce_handle_error`; exported real-mode entry helpers `__machine_check_early_realmode_p7/p8/p9/p10`.

Control flow: the platform-specific entry chooses a CPU generation table and passes SRR1/DSISR into `mce_handle_error`. Load/store errors use DSISR table matches; instruction errors use SRR1 masks. For recoverable SLB/ERAT/TLB events outside guests, the handler flushes or reloads the relevant translation structures. It fills `mce_error_info` with type, subtype, class, severity, initiator, and sync flag, derives effective and physical addresses where valid, and for UE may analyze the faulting instruction or consult exception-table/platform recovery hooks. Finally it calls `save_mce_event` with the handled decision.

State and persistence: no durable storage; state changes are translation-cache flushes, possible NIP fixup, PACA MCE event creation, and later memory-failure side effects from common code.

Dependencies and integration: depends on PowerPC real-mode page-table walking, hash/radix MMU distinction, SLB shadow routines, `analyse_instr`, KVM guest state in PACA, CPU-specific SRR1/DSISR definitions, and `ppc_md.mce_check_early_recovery`.

Risks: page-table lookup in real mode can race with updates; guest context intentionally avoids recovery and address lookup; table order matters because multiple DSISR bits may be set and UE entries must win; async store/link errors on P9/P10 need special SRR1 routing; wrong severity/class causes panic or missed isolation.

Test signals: inject SLB/ERAT/TLB parity or multihit errors, UE instruction and load/store faults, POWER9 paste spurious MCE, async real-address store errors, guest MCEs, and SCOM/OPAL early recovery paths.
