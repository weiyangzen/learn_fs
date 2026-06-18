# sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/usnic_debugfs.h

Purpose: debugfs API declarations for usNIC.

Important APIs: declares module-level init/exit and per-flow add/remove helpers accepting `struct usnic_ib_qp_grp_flow`.

Control flow: `usnic_ib_main.c` calls init/exit at module load/unload; `usnic_ib_qp_grp.c` calls flow add/remove around firmware filter lifetime.

State and persistence: no state in the header; implementation owns dentries and per-flow debugfs fields.

Dependencies and integration: includes `usnic_ib_qp_grp.h`, tying debugfs entries to QP group flow objects.

Risks: callers must pair add/remove exactly with QP flow allocation/freeing.

Test signals: compile linkage and debugfs entries appearing and disappearing with QP group flows.
