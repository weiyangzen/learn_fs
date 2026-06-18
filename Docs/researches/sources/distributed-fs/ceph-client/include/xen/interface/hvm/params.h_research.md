# sources/distributed-fs/ceph-client/include/xen/interface/hvm/params.h

Purpose: declares the index space and encoded values for `HVMOP_set_param` and `HVMOP_get_param`.

Important APIs/types/functions: `HVM_PARAM_CALLBACK_IRQ` and callback encodings for GSI, PCI INTx, x86 vector, and ARM PPI; `HVM_PARAM_STORE_PFN`, `HVM_PARAM_STORE_EVTCHN`, `HVM_PARAM_PAE_ENABLED`, `HVM_PARAM_IOREQ_PFN`, `HVM_PARAM_BUFIOREQ_PFN`, `HVM_PARAM_TIMER_MODE` with `HVMPTM_*` modes, `HVM_PARAM_HPET_ENABLED`, `HVM_PARAM_IDENT_PT`, `HVM_PARAM_DM_DOMAIN`, `HVM_PARAM_ACPI_S_STATE`, `HVM_PARAM_VM86_TSS`, `HVM_PARAM_VPT_ALIGN`, `HVM_PARAM_CONSOLE_PFN`, `HVM_PARAM_CONSOLE_EVTCHN`, and `HVM_NR_PARAMS`.

Control flow: builders and guests use `xen_hvm_param` from `hvm_op.h` with these indexes to publish shared pages, event channels, callback routing, timer behavior, and device-model ownership.

State and persistence: parameter values are per-domain Xen state and persist until changed or the domain exits. The XenStore page, console page, and IOREQ pages referenced here point to other shared-memory protocols.

Dependencies and integration points: includes `xen/interface/hvm/hvm_op.h`. Integrates with event channels, XenStore, HVM console, virtual timers, HPET, device models, and boot setup.

Risks: callback value packing differs by architecture. `HVM_PARAM_CALLBACK_TYPE_VECTOR` must be gated by `XENFEAT_hvm_callback_vector`. Wrong PFN/event-channel pairing breaks console, XenStore, or device-model I/O.

Test signals: HVM boot with XenStore and console online, timer-mode behavior under vCPU preemption, event-channel interrupt delivery for each supported callback type, and parameter boundary tests up to `HVM_NR_PARAMS`.
