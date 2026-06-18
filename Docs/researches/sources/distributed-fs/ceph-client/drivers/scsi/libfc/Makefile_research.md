# sources/distributed-fs/ceph-client/drivers/scsi/libfc/Makefile

Purpose: defines how the Fibre Channel libfc library object is built when `CONFIG_LIBFC` is enabled.

Important build API: `obj-$(CONFIG_LIBFC) += libfc.o` makes libfc conditional on kernel config. `libfc-objs` composes the library from `fc_libfc.o`, discovery, exchange, ELS/CT, frame, local-port, remote-port, FCP, and NPIV objects.

Control flow role: this file controls link composition, not runtime behavior. It ensures cross-file symbols such as exchange manager APIs, discovery callbacks, ELS/CT sending, FCP I/O, and NPIV support are linked into the single module/library object.

State and persistence: no runtime state. Build output depends on Kbuild and config state.

Dependencies and integration: integrates with kernel Kbuild and the SCSI/FCoE stack. Object order can matter for init/exit symbol availability and diagnostics but normal C linking resolves internal references across listed objects.

Risks and test signals: missing an object would cause unresolved symbols or disabled functionality; extra objects can change module footprint. Build tests with `CONFIG_LIBFC=m/y` are the primary signal, plus module load coverage for exported symbols used by LLDDs such as fcoe.
