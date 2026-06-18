# sources/distributed-fs/beegfs/meta/source/app/config/Config.cpp

Purpose: `Config.cpp` implements metadata-server-specific configuration defaults, parsing, implicit value derivation, and validation.

Important APIs/functions: The constructor initializes `sysTargetAttachmentMap` and calls `initConfig()`. `loadDefaults()` overlays metadata defaults such as `storeMetaDirectory`, xattr/ACL flags, worker/listener counts, chunk defaults, NUMA options, lock retry tuning, target chooser, quota options, file-event logging settings, daemonization, and PID file. `applyConfigMap()` parses string values into typed fields, validates `logType`, enforces `sysTargetOfflineTimeoutSecs >= 30`, preserves compatibility for `tuneDefaultNumStripeNodes`, and throws on unknown keys when requested. `initImplicitVals()` derives worker/comm-slave counts, chooser enum, interface list, socket buffers, auth hash, and target-attachment map.

Control flow: Parsing iterates the inherited config map, handles known keys, erases consumed entries, and optionally reports unknown entries. The target attachment map is loaded from a file into a string map and converted to `TargetMap`. `initTuneTargetChooserNum()` maps string names to enum values and rejects unsupported values, including `randomintranode`.

State and persistence behavior: The object stores runtime config only. It reads optional files: config file, interface list, auth file through the base class, and `sysTargetAttachmentFile`. `createDefaultCfgFilename()` uses `/etc/beegfs/beegfs-meta.conf` if present.

Dependencies/integration: `App` consumes almost every getter. `UnitTk` parses human sizes; `StringTk` parses booleans/integers; `MapTk` and `StorageTk` load attachment files. Risks include silent truncation because several byte-size fields are stored as `unsigned` after `int64_t` parsing, invalid target chooser names preventing startup, and ACL requiring xattrs checked later in `App`.

Test signals: Metadata config tests in the build target likely cover parts of this, but this subset does not include them.
