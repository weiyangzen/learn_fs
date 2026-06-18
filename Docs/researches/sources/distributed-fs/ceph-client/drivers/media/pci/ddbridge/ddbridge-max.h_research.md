# sources/distributed-fs/ceph-client/drivers/media/pci/ddbridge/ddbridge-max.h

Purpose: declares ddbridge MAX support entry points used by the core.

Important APIs/types/functions: `ddb_lnb_init_fmode()` changes link-level LNB frontend emulation mode; `ddb_fe_attach_mxl5xx()` attaches MXL5xx MAX frontends; `ddb_fe_attach_mci()` attaches MCI/SX8 frontends based on port type.

Control flow: included by `ddbridge-core.c` for frontend attachment and sysfs fmode changes, and implemented by `ddbridge-max.c`.

State and persistence: the header declares no state; implementations mutate `struct ddb_link.lnb`.

Dependencies/integration: includes `ddbridge.h` for `struct ddb`, `ddb_link`, and `ddb_input`.

Risks and test signals: signature drift breaks core builds. Runtime validation belongs to MAX frontend attach and fmode/LNB tests.
