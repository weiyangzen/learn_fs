# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_2401_system/host/ibuf_ctrl.c

Purpose: defines per-IBUF-controller process counts for the CSS 2401 input buffer controller block.

Important APIs/types/functions: `N_IBUF_CTRL_PROCS` maps three controller IDs to 8, 4, and 4 supported processes.

Control flow: static initialization only. Consumers use the array to bound process-register loops.

State and persistence: read-only runtime constant.

Dependencies and integration: includes `system_global.h` and `ibuf_ctrl_global.h`; integrates IBUF controller host code with generated system IDs.

Risks and test signals: wrong counts lead to invalid register access or incomplete state collection. Tests should cover all IBUF controller IDs and process loop bounds.
