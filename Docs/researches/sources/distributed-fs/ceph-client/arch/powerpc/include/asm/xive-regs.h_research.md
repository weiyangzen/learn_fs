<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/xive-regs.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/xive-regs.h

Purpose: Defines XIVE ESB and TIMA MMIO offsets, bit fields, and side-effect operation codes.

Important APIs/types/functions: ESB offsets such as `XIVE_ESB_STORE_EOI`, `XIVE_ESB_GET`, `XIVE_ESB_SET_PQ_*`, ordering offset `XIVE_ESB_LD_ST_MO`, PQ values, TIMA quadrants `TM_QW*`, byte/word offsets, QW word-2 bit masks, special TM operation offsets, and NSR field masks.

Control flow: XIVE code manipulates interrupt source P/Q state via 8-byte MMIO loads/stores and uses TIMA byte/word operations to acknowledge, pull/push contexts, and manage OS/HV/user interrupt state.

State and persistence: All state is hardware MMIO state: ESB P/Q pending bits, queue context validity, CPPR/IPB/NSR bytes, and TIMA context registers.

Dependencies and integration points: Depends on PowerPC bit macros and XIVE hardware/firmware programming models. Integrated by native, spapr, KVM, and xmon XIVE code.

Risks: Many offsets have side effects and require exact access sizes. Missing load-after-store ordering can break StoreEOI. Misusing QW permissions can corrupt interrupt context.

Test signals: XIVE interrupt delivery, EOI/retrigger tests, StoreEOI ordering checks, KVM XIVE tests, and hardware boot on POWER9/POWER10.

Source read size: 134 lines, 5083 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/xive-regs.h -->
