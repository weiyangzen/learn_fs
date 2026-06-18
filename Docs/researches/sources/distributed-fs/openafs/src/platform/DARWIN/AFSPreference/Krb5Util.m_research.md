# Research: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/Krb5Util.m

Purpose: implements Kerberos ticket acquisition and renewal for aklog workflows.

Important APIs and control flow: `getNewTicketIfNotPresent` calls `KLCacheHasValidTickets`, creates login options when no valid tickets exist, copies default login options on older SDKs, then calls `KLAcquireNewInitialTickets`. It throws for non-cancel Kerberos failures. `renewTicket:renewTime:` creates login options, reads current ticket expiration, and renews when seconds-to-expire is below the threshold. On newer SDKs it uses raw krb5 APIs to get renewed creds and store them; on older SDKs it uses `KLRenewInitialTickets`.

State and persistence: mutates the user's default Kerberos credential cache. No application-level state is stored.

Dependencies and integration: Foundation, KerberosLogin, Kerberos/krb5, dispatch once for krb5 context. Used by `AFSPropertyManager` before `aklog`.

Risks: error handling overwrites `kstatus` several times and may miss intermediate failures. Some krb5 resources such as creds contents are not fully freed in the visible code. SDK macro branches mean behavior differs across build targets. Interactive acquisition can block UI callers.

Test signals: no-ticket acquisition, user-cancel nonthrow behavior, default login option propagation, near-expiry renewal, krb5 cache store failures, and old/new SDK compile paths.
