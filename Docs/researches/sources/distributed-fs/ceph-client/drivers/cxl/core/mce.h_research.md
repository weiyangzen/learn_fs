# sources/distributed-fs/ceph-client/drivers/cxl/core/mce.h

Purpose: declares the CXL MCE notifier registration contract and provides a configuration stub when CXL MCE handling is not compiled. It lets mailbox/memdev setup code call one API independent of `CONFIG_CXL_MCE`.

Important APIs, types, and functions: the only API is `devm_cxl_register_mce_notifier(struct device *dev, struct notifier_block *mce_notifier)`. With `CONFIG_CXL_MCE`, the implementation lives in `mce.c`. Without it, the inline stub returns `-EOPNOTSUPP`.

Control flow: including code can call the helper during device-state creation. A real build registers a notifier and attaches a devm cleanup action; a disabled build receives `-EOPNOTSUPP`, allowing callers to warn or continue without alias-specific MCE handling.

State and persistence behavior: the header has no state. It defines the lifetime expectation that the notifier block is owned by the caller and remains valid until devm teardown.

Dependencies and integration points: depends on `<linux/notifier.h>`. It is included by `mbox.c`, which stores the notifier block in `struct cxl_memdev_state` and treats `-EOPNOTSUPP` as non-fatal.

Risks: callers must not treat every nonzero return as fatal without preserving the `-EOPNOTSUPP` distinction, or CXL memdev creation would fail on builds that intentionally omit MCE support. The header does not validate notifier storage lifetime; that remains a caller responsibility.

Test signals: compile both config variants, verify the disabled stub is inlined and returns `-EOPNOTSUPP`, and verify enabled builds link against `mce.c` and register/unregister through devm.
