# sources/distributed-fs/orangefs/src/client/sysint/init-vars.h
## sources/distributed-fs/orangefs/src/client/sysint/init-vars.h

**Purpose:** Declares sysint globals initialized during client startup.

**APIs and control flow:** Header guard `__INIT_VARS_H` protects a single declaration: `extern int relatime_timeout;`.

**State and dependencies:** No dependencies beyond C linkage. The declaration is consumed by initialization and any code enforcing OrangeFS relatime update behavior.

**Risks and tests:** As the shared declaration for a mutable global, it should remain minimal to avoid coupling. Test signals are indirect through initialization and atime-update paths. Adding more globals here should include clear ownership and lifecycle documentation.
