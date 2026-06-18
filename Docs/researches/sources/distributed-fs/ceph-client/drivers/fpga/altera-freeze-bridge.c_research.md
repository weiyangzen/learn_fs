## sources/distributed-fs/ceph-client/drivers/fpga/altera-freeze-bridge.c

Purpose: this FPGA bridge driver controls an Altera freeze bridge in FPGA fabric, isolating a reconfigurable region from buses during partial reconfiguration.

Important APIs and functions: `struct altera_freeze_br_data` tracks MMIO base and cached enable state. `altera_freeze_br_do_freeze()` issues `FREEZE_REQ`, waits for `FREEZE_REQ_DONE`, then asserts `RESET_REQ`. `altera_freeze_br_do_unfreeze()` clears control, issues `UNFREEZE_REQ`, and waits for `UNFREEZE_REQ_DONE`. `altera_freeze_br_req_ack()` polls status and illegal-request registers. `altera_freeze_br_enable_set()` maps FPGA bridge enable semantics to freeze/unfreeze operations and uses image-info timeouts when present.

Control flow: probe requires an OF node, maps resource 0, validates bridge CSR version against supported or official values, initializes cached enable state from status, registers an FPGA bridge named `freeze`, and stores it as driver data. Remove unregisters the bridge.

State and persistence: hardware state lives in the CSR status/control/illegal-request registers. The cached `enable` boolean is updated only after successful operations and is returned by `enable_show()`. Illegal request status is cleared by writing one to the illegal-request register.

Dependencies and integration: it depends on MMIO, platform devices, OF compatible `altr,freeze-bridge-controller`, and the FPGA bridge framework. It participates in `fpga_region` bridge lists during partial reconfiguration.

Risks: timeout defaults to zero if no `fpga_image_info` is attached, resulting in only one poll iteration. `enable_show()` returns cached state, not a fresh CSR read after probe. Illegal-request clearing assumes write-one behavior and only logs if clearing fails. The driver rejects unexpected versions, so compatible hardware revisions require updates.

Test signals: validate freeze/unfreeze from all legal starting states, illegal-request reporting and clearing, timeout behavior with image-specific enable/disable timeouts, revision rejection, and bridge state after failed operations.
