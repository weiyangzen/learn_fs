# sources/distributed-fs/ceph-client/drivers/scsi/be2iscsi/Makefile

Purpose: defines the Kbuild composition of the `be2iscsi` driver.

Important APIs/types/functions: `obj-$(CONFIG_BE2ISCSI) += be2iscsi.o` declares the composite object. `be2iscsi-y := be_iscsi.o be_main.o be_mgmt.o be_cmds.o` links transport/session logic, main HBA and I/O logic, firmware management helpers, and mailbox/MCC command helpers.

Control flow: Kbuild evaluates this file at build time only. Runtime initialization is provided by the linked C files, primarily `be_main.c`.

State and persistence: no runtime state is held here; it controls reproducible object composition from `.config`.

Dependencies and integration: must stay aligned with cross-file prototypes in `be.h`, `be_cmds.h`, `be_iscsi.h`, `be_main.h`, and `be_mgmt.h`.

Risks and test signals: object-list drift causes link failures or missing transport callbacks. Test signals are clean modular and built-in builds with `CONFIG_BE2ISCSI` enabled, plus ensuring all helper implementations referenced by the transport template and PCI driver are linked into the composite object.
