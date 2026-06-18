## sources/distributed-fs/eos/namespace/Constants.cc

Purpose: Defines namespace-wide constants declared in `Constants.hh`.

Important APIs and values: provides the single definition of `eos::QUOTA_NODE_FLAG` as `0x0001`.

Control flow: no executable control flow beyond static initialization of a constant.

State and persistence: no runtime mutable state; this value is a compile/link-time ABI-visible symbol used to mark quota-node containers.

Dependencies and integration: includes `namespace/Constants.hh` and participates in `EosNsCommon-Objects`.

Risks: changing the numeric flag can reinterpret persisted metadata flags. Because it is an external constant rather than `constexpr`, consumers require this object to link.

Test signals: link tests for `QUOTA_NODE_FLAG` and metadata tests verifying quota-node flag interpretation.
