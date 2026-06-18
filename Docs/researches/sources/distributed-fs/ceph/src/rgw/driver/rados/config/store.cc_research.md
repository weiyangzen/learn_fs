# sources/distributed-fs/ceph/src/rgw/driver/rados/config/store.cc

Purpose: Provides construction and destruction for `RadosConfigStore`, including initialization of the underlying librados client used by all config-store operations.

Important APIs/types/functions: `RadosConfigStore::RadosConfigStore()` stores a `unique_ptr<ConfigImpl>`. The destructor is defaulted. `create_config_store()` allocates `ConfigImpl`, calls `rados.init_with_context()`, connects, and returns the store or null on failure.

Control flow: Factory reads config from `dpp->get_cct()`, initializes the client, logs connection failures, and only exposes a store after a successful `rados.connect()`.

State/persistence: The file does not write config objects directly. It establishes the long-lived librados connection held by `ConfigImpl` and later used for realm/period/zone operations and watchers.

Dependencies/integration: Depends on librados, `ConfigImpl`, `store.h`, `DoutPrefixProvider`, and Ceph error formatting.

Risks: On `connect()` failure after successful init, the partially initialized `ConfigImpl` is destroyed; callers must handle null. There is no retry/backoff in the factory.

Test signals: Simulate init/connect failures, verify null return and logging, and verify a successful store can perform subsequent config operations.
