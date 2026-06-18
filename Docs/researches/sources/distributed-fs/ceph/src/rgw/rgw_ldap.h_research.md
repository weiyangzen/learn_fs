# sources/distributed-fs/ceph/src/rgw/rgw_ldap.h

Purpose: Declares RGW LDAP integration, with an OpenLDAP-backed helper when available and a stub helper when RGW is built without OpenLDAP support.

Important APIs and types: `rgw::LDAPHelper` stores LDAP URI, service bind DN/password, search DN/filter, DN attribute, optional AD mode flag, the `LDAP*` connection, and a mutex. Key methods are `init()`, `bind()`, `rebind()`, `simple_bind()`, `auth()`, and the destructor. The global helper `parse_rgw_ldap_bindpw()` loads the bind password from config.

Control flow: OpenLDAP builds initialize a protocol v3 LDAP connection, disables referrals, performs service bind, and later authenticates users by search plus simple bind. Non-OpenLDAP builds expose the same constructor and methods but return `-ENOTSUP` for setup and `-EACCES` for auth.

State and persistence: `LDAPHelper` owns and unbinds one service LDAP connection. It creates temporary LDAP connections for user password checks. No RGW metadata is persisted here.

Dependencies and integration points: Guarded by `HAVE_OPENLDAP` and includes `ldap.h` with deprecated APIs enabled. Also includes Ceph context/debug/safe IO headers because the password parser is declared here. Used by RGW main initialization and auth paths.

Risks: The helper is synchronous and protected by a single mutex, so LDAP search throughput can serialize. The destructor unbinds the service connection but temporary bind behavior depends on `simple_bind()` always reaching unbind after initialize. Stub behavior should be surfaced clearly in configuration tests so LDAP auth is not silently expected in unsupported builds.

Test signals: Build-matrix tests should verify both OpenLDAP and no-OpenLDAP paths. Runtime tests should cover init option failures, bind failure mapping, rebind behavior, destructor cleanup, and thread serialization during auth.
