# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/security/VerifierGSS.java

Purpose: placeholder verifier type for RPCSEC_GSS.

Important APIs/types/functions: constructor, `read`, and `write`.

Control flow: constructor sets flavor to `RPCSEC_GSS`; read/write are empty TODO stubs.

State and persistence: no verifier body state; no persistence.

Dependencies and integration: selected by `Verifier.readFlavorAndVerifier` and emitted by `Verifier.writeFlavorAndVerifier`.

Risks: does not parse or serialize GSS verifier payloads, so using it without additional wrapping logic can leave wire bytes unread or responses incomplete.

Test signals: auth flavor recognition can be tested, but full GSS verifier behavior is unimplemented.
