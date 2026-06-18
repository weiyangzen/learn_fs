# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/SecurityUtilTestHelper.java

Purpose: Small test helper exposing package/private-adjacent security utility controls.

Important APIs/types/functions: `setTokenServiceUseIp(boolean)` and `isExternalKdcRunning()`.

Control flow: `setTokenServiceUseIp` delegates to `SecurityUtil.setTokenServiceUseIp`. `isExternalKdcRunning` checks JVM properties `externalKdc` equals `true` and `java.security.krb5.conf` is set.

State and persistence: mutates global `SecurityUtil` token-service behavior; reads system properties.

Dependencies/integration points: security token service construction and tests that optionally use an external Kerberos KDC.

Risks: global toggle can affect later tests if not reset; external KDC detection is property-based and does not validate the KDC itself.

Test signals: enables tests to force host/IP token service choices and conditionally run external-KDC scenarios.
