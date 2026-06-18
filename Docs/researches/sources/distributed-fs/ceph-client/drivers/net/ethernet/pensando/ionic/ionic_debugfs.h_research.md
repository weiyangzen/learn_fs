# sources/distributed-fs/ceph-client/drivers/net/ethernet/pensando/ionic/ionic_debugfs.h

Purpose: Declares Ionic debugfs lifecycle helpers and provides no-op stubs for non-debugfs builds.

Important APIs/types/functions: Public helpers cover global create/destroy, per-device add/delete, identity/sizes files, LIF add/delete, QCQ add/delete. Under `CONFIG_DEBUG_FS=n`, inline stubs preserve unconditional call sites.

State and dependencies: Includes `linux/debugfs.h` and references `struct ionic`, `struct ionic_lif`, and `struct ionic_qcq` through function prototypes.

Risks and test signals: Compile coverage must include debugfs enabled and disabled. Runtime tests should verify debugfs entries are recreated after reset and removed during queue/LIF/device teardown.
