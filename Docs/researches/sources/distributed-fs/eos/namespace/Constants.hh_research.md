## sources/distributed-fs/eos/namespace/Constants.hh

Purpose: Declares namespace constants shared across namespace components.

Important APIs and values: declares `extern const uint16_t QUOTA_NODE_FLAG`.

Control flow: header-only declaration with no runtime flow.

State and persistence: the constant is used as a bit in metadata flags and therefore participates in persisted container state semantics.

Dependencies and integration: includes `<stdint.h>` and exposes the symbol in namespace `eos`.

Risks: consumers must include the matching object definition. Header does not document bit ownership beyond the name, so flag collisions should be checked before adding more constants.

Test signals: compile tests including the header from C++ consumers and behavior tests for quota-node registration/removal.
