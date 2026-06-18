# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/security/CredentialsGSS.java

Purpose: placeholder credential type for RPCSEC_GSS auth flavor.

Important APIs/types/functions: constructor, `read`, and `write`.

Control flow: constructor sets flavor to `RPCSEC_GSS`; read/write are currently empty TODO stubs.

State and persistence: no body fields are stored; inherited length is not updated.

Dependencies and integration: selected by `Credentials.readFlavorAndCredentials` when the wire flavor is `RPCSEC_GSS`.

Risks: this does not actually parse or emit RPCSEC_GSS credential bodies, so GSS-protected traffic needs higher-level handling elsewhere or will leave bytes unread/missing. Tests should pin this limitation to avoid assuming complete GSS support.

Test signals: auth-info tests can verify flavor recognition, but full GSS credential behavior is unimplemented.
