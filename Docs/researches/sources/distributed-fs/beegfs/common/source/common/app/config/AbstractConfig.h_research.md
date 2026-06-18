<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/app/config/AbstractConfig.h -->
## sources/distributed-fs/beegfs/common/source/common/app/config/AbstractConfig.h

### Purpose
This header declares the shared base class for BeeGFS configuration parsers.

### Important APIs, Types, And Functions
`AbstractConfig` stores `configMap`, original argc/argv, and `cfgFile`. Protected hooks include `loadDefaults`, `applyConfigMap`, `initImplicitVals`, `initInterfacesList`, `initConnAuthHash`, `initSocketBufferSizes`, `loadFromFile`, `loadFromArgs`, `eraseFromConfigMap`, and `assignKeyIfNotZero`. Inline helpers redefine keys and test key matches with optional `--` prefix and case-insensitivity.

### Control Flow
Derived constructors call `initConfig` after their own construction so virtual default/application hooks dispatch correctly.

### State, Persistence, And Dependencies
Configuration state persists in inherited `ICommonConfig` fields after `configMap` entries are consumed. Dependencies include `Common`, `MapTk`, `InvalidConfigException`, `ConnAuthFileException`, and `ICommonConfig`.

### Integration Points
Concrete app configs extend this class to add service-specific keys while reusing common networking/logging/auth settings. Free function `loadNetworkList` is declared here for consumers that need CIDR filters.

### Risks
Calling `initConfig` from the base constructor would be unsafe; the comment documents that derived classes must call it. `addDashes` changes both key shape and matching case-sensitivity, so command-line style parsers must use it intentionally.

### Test Signals
Derived config tests should verify virtual hook ordering, dashed-key matching, map cleanup of consumed keys, and that service-specific unknown keys are handled by derived `applyConfigMap`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/app/config/AbstractConfig.h -->
