<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/app/config/AbstractConfig.cpp -->
## sources/distributed-fs/beegfs/common/source/common/app/config/AbstractConfig.cpp

### Purpose
`AbstractConfig.cpp` implements shared configuration loading, defaults, parsing, validation, authentication-file hashing, socket buffer post-processing, and network-list loading.

### Important APIs, Types, And Functions
Key methods are `initConfig`, `loadDefaults`, `applyConfigMap`, `initImplicitVals`, `initInterfacesList`, `initConnAuthHash`, `initSocketBufferSizes`, `eraseFromConfigMap`, `loadFromFile`, `loadFromArgs`, `assignKeyIfNotZero`, and free function `loadNetworkList`.

### Control Flow
Initialization first loads defaults and command-line args to discover `cfgFile`. If a config file is set, it clears the map and reloads defaults, file entries, then command-line overrides. `applyConfigMap` consumes recognized keys, maps deprecated TCP/UDP port settings into unified ports, validates timeout tuple sizes, and throws on unknown keys when enabled. Authentication hashing reads up to 1024 bytes of binary auth file content, optionally retries with elevated saved fs ids on `EACCES`, rejects missing/short files unless authentication is explicitly disabled, and computes `HashTk::authHash`.

### State, Persistence, And Dependencies
Parsed settings persist in inherited `ICommonConfig` fields and `cfgFile`; `configMap` is transient and consumed during parsing. Dependencies include `StringTk`, `StorageTk`, `MapTk`, `System`, `HashTk`, logging, and filesystem/syscall access.

### Integration Points
All concrete service configs inherit these defaults and parsing rules. Network listeners consume UDP/TCP/RDMA buffer sizes, ports, filters, authentication hash, timeout values, and RDMA TOS settings.

### Risks
Authentication now fails closed unless `connDisableAuthentication` is true, so deployments without `connAuthFile` fail early. Deprecated per-protocol ports can conflict with unified settings. Utility tools tolerate a five-field `connRDMATimeouts` value by ignoring it, which can hide misconfiguration. `assignKeyIfNotZero` rejects zero only when exception mode is enabled.

### Test Signals
Tests should cover precedence of defaults/file/args, unknown-key behavior, deprecated port reconciliation, timeout tuple validation, auth file missing/empty/permission paths, socket buffer legacy derivation, interface file/list exclusivity, and invalid CIDR logging in `loadNetworkList`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/app/config/AbstractConfig.cpp -->
