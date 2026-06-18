# sources/distributed-fs/ceph-client/drivers/media/pci/ddbridge/ddbridge-dummy-fe.h

Purpose: declares the ddbridge dummy frontend attach API. It is a small include guard around the DVB frontend includes and the single constructor `ddbridge_dummy_fe_qam_attach()`.

Important APIs/types/functions: the exported API returns `struct dvb_frontend *` or `NULL` on allocation failure. Callers own the returned frontend through normal DVB frontend registration and release semantics.

Control flow: included by `ddbridge-core.c` and implemented by `ddbridge-dummy-fe.c`; no control flow beyond compile-time declaration.

State and persistence: no state is declared here beyond the function contract.

Dependencies/integration: includes `<linux/dvb/frontend.h>` and `<media/dvb_frontend.h>`, tying it directly to DVB core types.

Risks and test signals: risk is limited to API drift with the implementation. Test signals are successful compile/link when dummy frontend support is built and correct symbol resolution when `dvb_attach()` is used.
