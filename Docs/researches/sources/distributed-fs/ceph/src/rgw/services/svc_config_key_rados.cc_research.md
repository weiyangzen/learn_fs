<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_config_key_rados.cc -->
# sources/distributed-fs/ceph/src/rgw/services/svc_config_key_rados.cc

Purpose: Implements monitor config-key reads through `librados::Rados::mon_command()`.

Important APIs, types, and functions: `do_start()` records whether the monitor connection may be insecure via `rgw_check_secure_mon_conn()`. `warn_if_insecure()` emits a cluster log and local error log at most once using `atomic_flag`. `get()` builds a JSON `config-key get` command and returns the monitor response in a `bufferlist`.

Control flow: Startup checks monitor transport security. Each `get()` sends a monitor command. If the monitor returns an error, it is propagated. If the caller marked the key as secure, the service emits a one-time warning when the monitor connection is potentially insecure.

State and persistence: The service stores a RADOS pointer, a boolean for insecure-connection possibility, and an atomic one-shot warning flag. The fetched config-key data remains monitor-persisted.

Dependencies and integration points: Depends on `rgw_check_secure_mon_conn()`, `rgw_clog_warn()`, `librados::Rados`, and Ceph monitor command JSON format.

Risks and test signals: The JSON command is string-concatenated, so unusual key strings need validation at higher layers or escaping assumptions from monitor APIs. Secure reads over insecure monitor connections only warn; they do not fail. Tests should cover missing keys, successful values, secure warning once, and startup with secure/insecure monitor modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_config_key_rados.cc -->
