# sources/distributed-fs/beegfs/meta/source/app/config/Config.h

Purpose: `Config.h` declares metadata daemon configuration fields and typed getters.

Important APIs/types: `TargetChooserType` enumerates randomized, round-robin, random-robin, random-inter-node, and random-intra-node chooser modes, though the implementation disallows random-intra-node. `Config` derives from `AbstractConfig` and overrides `loadDefaults()`, `applyConfigMap()`, and `initImplicitVals()`. It exposes getters for network interface filters, metadata storage paths and UUID, xattr/ACL behavior, worker/listener/buffer tuning, default striping, NUMA, lock retry policy, mirror behavior, disposal GC period, chunk balancing, quota, offline timeout, user set pattern, daemonization, PID file, xattr-list limiting, and file-event logging target/persistence.

Control flow contract: Private helpers derive the target attachment map and target chooser enum. Public setters are intentionally limited: quota enforcement and xattr-list limit can be changed after parsing.

State and persistence behavior: Persistent inputs referenced by the config include metadata directory, filesystem UUID, target attachment file, auth/interface files from the base class, PID file, and file-event persistence directory. The owned `TargetMap* sysTargetAttachmentMap` is deleted by the destructor.

Dependencies/integration: `App`, `InternodeSyncer`, file-event logging, disposal GC, worker creation, and storage initialization all depend on these accessors. The header acts as the stable contract for metadata service tuning.

Risks and test signals: Many related settings are independent booleans or unsigned integers, so cross-field validation is split between `Config.cpp` and `App.cpp`. The raw `TargetMap*` requires careful ownership. Human-size values exposed as unsigned or uint64 can mask negative/overflow errors if not validated at parse time.
