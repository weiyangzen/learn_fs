# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/main/resources/kms-default.xml

## Purpose
`kms-default.xml` documents and supplies default KMS configuration values.

## Important APIs, Types, and Functions
Properties define HTTP port/host/admin ACLs, SSL enablement, HTTP thread/header/temp/backlog/idle settings, backing key provider URI, Java keystore password file, KMS cache enablement and TTLs, audit aggregation window, simple or Kerberos authentication, signer secret provider options including ZooKeeper, audit logger class, per-key authorization enablement, and encrypted-key cache sizing/fill/expiry settings.

## Control Flow
`KMSConfiguration` adds this resource as a default resource, and `getKMSConf` combines it with core-site and kms-site. Operators should copy changed properties to `kms-site.xml` rather than editing this file.

## State and Persistence
This is persisted default configuration. It does not store runtime state, but defaults directly influence provider persistence location, cache behavior, auth mode, and logging behavior.

## Dependencies and Integration Points
Keys mirror constants in `KMSConfiguration`, Hadoop HTTP server keys, Hadoop authentication keys, and Eager EEK cache keys. `KMSWebServer`, `KMSWebApp`, `KMSAudit`, and `KMSAuthenticationFilter` consume these values.

## Risks
Defaults favor local/simple operation: HTTP binds to all interfaces on port 9600, SSL is disabled, authentication is simple, and provider URI points to `${user.home}/kms.keystore`. Production deployments must override these. Typos in descriptions such as "maxmimum" are harmless but documentation-facing.

## Test Signals
Tests should verify defaults load, constants match property names, production overrides in `kms-site.xml` take precedence, auth defaults are usable in MiniKMS, and cache/audit defaults match Java constants.
