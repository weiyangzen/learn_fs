# Research: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/Krb5Util.h

Purpose: declares Kerberos helper APIs for acquiring and renewing tickets before AFS token acquisition.

Important APIs: `+getNewTicketIfNotPresent` ensures there are valid Kerberos tickets, and `+renewTicket:renewTime:` renews tickets when expiration is near. The class imports both legacy KerberosLogin and Kerberos headers.

Control flow and persistence: no local persistence. It operates on the user's default Kerberos credential cache and login dialogs.

Dependencies and integration: `AFSPropertyManager aklog:noKerberosCall:` calls `getNewTicketIfNotPresent` before running `aklog`. Backgrounder code can use renew preferences defined in `global.h`.

Risks: KerberosLogin APIs are legacy and gated by SDK version macros. Caller behavior depends on interactive login availability.

Test signals: valid ticket cache, empty cache with successful login, user cancel, expired-but-renewable ticket, nonrenewable ticket, and SDK-version-specific compilation.
