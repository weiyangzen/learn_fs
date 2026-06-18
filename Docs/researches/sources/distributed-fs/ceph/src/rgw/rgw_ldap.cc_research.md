# sources/distributed-fs/ceph/src/rgw/rgw_ldap.cc

Purpose: Implements LDAP password loading and, when OpenLDAP is available, LDAP user authentication for RGW.

Important APIs and functions: `parse_rgw_ldap_bindpw()` reads the configured bind password secret file. `rgw::LDAPHelper::auth()` builds an LDAP search filter for a uid, searches under the configured search DN, and verifies the supplied password by binding as the discovered user DN.

Control flow: Bind password parsing reads `rgw_ldap_secret`, trims whitespace, and zeroizes the stack buffer. Authentication chooses a Microsoft AD style filter if `msad` is enabled, otherwise uses either a default `(<dnattr>=<uid>)`, a configured filter containing `@USERNAME@`, or an AND-combined custom filter plus uid condition. It serializes access with `mtx`, searches the existing LDAP connection, attempts one rebind and retry on search failure, then calls `simple_bind()` on a temporary LDAP connection for password verification.

State and persistence: The helper owns a persistent `LDAP*` connection initialized and service-bound by code in the header. It does not persist RGW state. The password buffer from the secret file is zeroed after reading.

Dependencies and integration points: Depends on OpenLDAP when `HAVE_OPENLDAP` is set, Ceph config and safe file IO, Boost trim, and RGW auth setup in `rgw_main`. Without OpenLDAP, the header provides a stub returning unsupported/access denied.

Risks: Filter construction concatenates uid into LDAP filters without visible escaping in this file, which is a classic LDAP injection concern unless sanitized by callers or config constraints. `ldap_get_dn()` return handling assumes a DN is returned. Search errors collapse to `-EACCES` after one rebind, which can obscure operational LDAP failures from users.

Test signals: Tests should cover secret file trimming/zeroization behavior, default and custom filter construction, `@USERNAME@` substitution, search miss handling, rebind retry, password bind failures, OpenLDAP-disabled behavior, and injection-shaped usernames.
