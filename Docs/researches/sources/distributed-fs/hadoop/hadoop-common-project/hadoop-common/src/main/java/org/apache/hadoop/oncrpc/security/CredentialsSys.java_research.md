# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/security/CredentialsSys.java

Purpose: credential implementation for ONC RPC `AUTH_SYS`, carrying host, uid, gid, auxiliary gids, and stamp.

Important APIs/types/functions: constructor, getters/setters for uid/gid/stamp/host, `read`, and `write`.

Control flow: static initialization captures local host name. `read` consumes credential length, stamp, hostname string, uid, gid, aux group count, and each aux gid. `write` computes padded credential length, writes stamp, hostname, uid, gid, aux group count, and aux gid list.

State and persistence: mutable credential fields in memory; no persistence.

Dependencies and integration: consumed by `SysSecurityHandler` and request parsing. Uses `XDR` string alignment and UTF-8 hostname bytes.

Risks: static host lookup failure throws at class load. `read` trusts aux group count and can allocate large arrays from malformed input. Credential length is computed but not validated against bytes read. Hostname setter is test-visible only.

Test signals: `TestCredentialsSys` covers length calculation, host/stamp fields, uid/gid/aux groups, and round trips.
