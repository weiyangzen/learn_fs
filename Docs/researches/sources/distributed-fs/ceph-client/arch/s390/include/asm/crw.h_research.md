<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/crw.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/crw.h

Purpose: Defines channel-report-word structures and handler registration.

Important APIs/types/functions: `struct crw`, `crw_handler_t`, `crw_register_handler()`, `crw_unregister_handler()`, `crw_handle_channel_report()`, resource codes, and event reporting codes. Source-visible declarations include: #define _ASM_S390_CRW_H; struct crw {; typedef void (*crw_handler_t)(struct crw *, struct crw *, int);; extern int crw_register_handler(int rsc, crw_handler_t handler);; extern void crw_unregister_handler(int rsc);; extern void crw_handle_channel_report(void);; void crw_wait_for_channel_report(void);; #define NR_RSCS 16; #define CRW_RSC_MONITOR 0x2 /* monitoring facility */; #define CRW_RSC_SCH 0x3 /* subchannel */.

Control flow: Machine-check/channel-report handling decodes one or two CRWs and dispatches to resource-specific registered handlers.

State and persistence behavior: Persistent state is the handler table and pending hardware report state.

Dependencies and integration points: Direct includes are #include <linux/types.h>. Integrated with Integrates CSS, channel path, subchannel, monitoring, and configuration-alert handling..

Risks: Handlers must tolerate chained reports and asynchronous hardware change; wrong resource codes can miss reconfiguration events.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 55 lines, 1858 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/crw.h -->
