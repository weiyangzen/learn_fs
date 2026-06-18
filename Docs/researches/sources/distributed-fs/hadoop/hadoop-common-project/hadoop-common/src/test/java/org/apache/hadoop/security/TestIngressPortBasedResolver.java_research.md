# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestIngressPortBasedResolver.java

Purpose: Unit test for SASL QOP selection by inbound server port.

Important APIs/types/functions: `IngressPortBasedResolver`, `setConf`, `getServerProperties`, `Sasl.QOP`, and configuration keys `ingress.port.sasl.*`.

Control flow: configures ports 444, 555, 666, and 777, with explicit QOP values for three of them. Assertions verify `authentication` maps to `auth`, `authentication,privacy` to `auth,auth-conf`, `privacy` to `auth-conf`, configured port without property defaults to privacy, and unknown port defaults to authentication.

State and persistence: resolver configuration only.

Dependencies/integration points: Hadoop RPC/SASL server property resolution.

Risks: string mapping is brittle; no invalid property or malformed port tests.

Test signals: confirms per-port QOP policy resolution and defaults.
