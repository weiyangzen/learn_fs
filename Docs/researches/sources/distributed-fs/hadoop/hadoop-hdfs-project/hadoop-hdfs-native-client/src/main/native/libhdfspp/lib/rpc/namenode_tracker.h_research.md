# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/rpc/namenode_tracker.h

Purpose: declares `HANamenodeTracker`, a helper that maps a failed endpoint to an alternate HA NameNode.

Important APIs and types: constructor, destructor, `is_enabled`, `is_resolved`, `GetFailoverAndUpdate`, private active/standby endpoint checks, active/standby `ResolvedNamenodeInfo`, and `swap_lock_`.

Control flow: `RpcEngine` owns the tracker when HA config is detected and asks it for alternate endpoints on failover retries. The call mutates internal active/standby state.

State and persistence: in-memory enabled/resolved flags, `IoService`, event handlers, active/standby info, and mutex. No persistent state across process restarts.

Dependencies and integration: includes event and NameNode info helpers plus Boost endpoints. This is part of RPC retry/failover integration.

Risks and test signals: public `GetFailoverAndUpdate` always mutates state; callers needing read-only checks cannot use it safely. Tests should validate locking and behavior with more than two configured NameNodes.
