# sources/distributed-fs/ceph-client/drivers/firmware/imx/imx-scu-irq.c

Purpose: Handles SCU general interrupt notifications over mailbox and exposes notifier/status helpers plus a sysfs wakeup source report.

Important APIs/types/functions: Exports `imx_scu_irq_register_notifier()`, `imx_scu_irq_unregister_notifier()`, `imx_scu_irq_get_status()`, `imx_scu_irq_group_enable()`, and `imx_scu_enable_general_irq_channel()`. Message structs encode SCU IRQ status and enable RPC calls. `scu_irq_wakeup` tracks masks and wakeup status for nine groups.

Control flow: `imx_scu_enable_general_irq_channel()` derives the MU resource id from DT mailbox phandle, gets the global SCU IPC handle, allocates a mailbox client, requests `gip3`, creates `/sys/firmware/scu_wakeup_source/wakeup_src`, and initializes work. RX callback schedules work; work queries each IRQ group, records wake source, wakes the system, and calls registered notifiers.

State and persistence behavior: Global IPC handle, work item, notifier chain, wakeup kobject, MU resource id, and wakeup masks persist for the SCU lifetime. Firmware IRQ enable state is changed via RPC.

Dependencies and integration points: Depends on SCU RPC core, mailbox, DT aliases, firmware kobjects, PM wakeup, and blocking notifier chains.

Risks and test signals: `wakeup_source_show()` can return uninitialized/last buffer contents if no wakeup source is set. Group bounds are not explicitly checked in `imx_scu_irq_group_enable()`. Test IRQ enable/disable per group, mailbox events, notifier delivery, suspend wakeup reporting, and cleanup behavior.
