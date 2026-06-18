# sources/distributed-fs/ceph/src/rgw/rgw_client_io.cc

Purpose: implements basic RGW client I/O initialization and debug logging of request environment variables.

Important APIs/types/functions: `rgw::io::BasicClient::init(CephContext*)`.

Control flow: `init()` calls virtual/overridden `init_env(cct)` and returns immediately on error. At RGW debug level 20, it iterates through `get_env().get_map()`, wraps each key/value in `rgw::crypt_sanitize::env`, and logs sanitized environment values.

State/persistence: initializes per-client request environment state via `init_env()`. No durable state.

Dependencies/integration: `rgw_client_io.h`, crypt sanitization, RGW dout subsystem, `CephContext` debug configuration, and `RGWEnv` map access. Used by frontends before request processing/auth.

Risks: debug logging must remain sanitized because env contains credentials and signatures. `init_env()` failure skips logging and propagates the raw error. Logging every env variable at level 20 can be noisy but useful for auth/debug tests.

Test signals: successful and failing `init_env()` propagation, sanitized logging for authorization/security headers, no unsanitized secret leakage, and debug-level gating.
