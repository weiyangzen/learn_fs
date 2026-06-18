# sources/distributed-fs/ceph-client/drivers/media/pci/mgb4/mgb4_cmt.h

- Purpose: Declaration header for MGB4 CMT programming helpers.
- Important APIs/types/functions: `mgb4_cmt_set_vout_freq` and `mgb4_cmt_set_vin_freq_range` with vin/vout type includes.
- Control flow: Used by vout init/sysfs and vin sysfs to program clocking.
- State and persistence: No state; functions mutate hardware registers and endpoint fields.
- Dependencies and integration points: Integrates CMT code with vin/vout modules.
- Risks: Includes both vin and vout headers, so include-order cycles must stay benign.
- Test signals: Compile plus sysfs frequency tests.
