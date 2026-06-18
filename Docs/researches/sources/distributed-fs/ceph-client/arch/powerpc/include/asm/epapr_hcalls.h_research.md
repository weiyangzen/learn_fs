## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/epapr_hcalls.h

Purpose: provides inline C wrappers for ePAPR hypercalls issued through the PowerPC `sc 1` hypercall entry.

Important APIs/types/functions: declares `epapr_paravirt_enabled`, `epapr_hypercall_start`, `epapr_paravirt_early_init()`, interrupt hypercalls (`ev_int_set_config`, `ev_int_get_config`, `ev_int_set_mask`, `ev_int_get_mask`, `ev_int_eoi`, `ev_int_iack`), byte channel hypercalls, `ev_doorbell_send()`, `ev_idle()`, generic `epapr_hypercall()`, and convenience `epapr_hypercall0*` through `epapr_hypercall4()`.

Control flow: wrappers bind arguments to fixed registers, set r11 to the hypercall token, branch to `epapr_hypercall_start`, read return registers, and copy outputs to caller buffers. Byte-channel helpers marshal four big-endian 32-bit words. Generic paravirt wrappers pass up to eight input/output registers when enabled, otherwise return `EV_UNIMPLEMENTED`.

State and persistence: no local state, but hypercalls mutate hypervisor state such as interrupt configuration, masks, byte-channel queues, doorbells, and virtual CPU idle state.

Dependencies and integration: depends on UAPI ePAPR tokens, byte order helpers, errno, and the paravirt early initialization path. Used by embedded hypervisor interrupt, console/byte-channel, idle, and paravirtualized platform code.

Risks and test signals: register constraints and clobber lists are correctness-critical. Missing memory clobbers can reorder guest memory shared with the hypervisor. Test signals include ePAPR guest boot, interrupt config/mask/EOI paths, byte-channel send/receive, idle hypercall behavior, paravirt-disabled fallback, and compiler build coverage for GCC/Clang.
