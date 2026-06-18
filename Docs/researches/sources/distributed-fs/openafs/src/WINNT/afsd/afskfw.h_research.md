# sources/distributed-fs/openafs/src/WINNT/afsd/afskfw.h

## Purpose
`afskfw.h` is the public interface for the Windows Kerberos for Windows/OpenAFS bridge implemented by `afskfw.c`. It exposes initialization, availability checks, credential acquisition, token renewal/destruction, cell configuration, LSA principal access, and file credential-cache helper routines to the Windows logon provider and related utilities.

## Important APIs, Types, And Constants
The header imports OpenAFS authentication, cell configuration, cache-manager config, and rxkad definitions. It defines cell and host size constants (`CELL_MAXNAMELEN`, `MAXHOSTCHARS`, `MAXHOSTSPERCELL`), the AFSD service name `TRANSARCAFSDAEMON`, Kerberos/AFS compatibility error values, probe credentials (`PROBE_USERNAME`, `PROBE_PASSWORD_LEN`), and `DO_NOT_REGISTER_VARNAME`, which suppresses pts auto-registration during selected logon paths. Exported functions include `KFW_AFS_get_cred`, `KFW_AFS_renew_expiring_tokens`, `KFW_AFS_renew_token_for_cell`, `KFW_AFS_destroy_tickets_for_cell`, `KFW_AFS_destroy_tickets_for_principal`, `KFW_probe_kdc`, `KFW_AFS_get_cellconfig`, and SYSTEM/user ccache copy helpers reserved for `afslogon.dll`.

## Control Flow And Integration
The header separates general KFW operations from `afslogon.dll`-only cache migration calls. Consumers typically call `KFW_is_available` or `KFW_initialize`, then use `KFW_AFS_get_cred` for integrated token creation, renewal functions during credential maintenance, and destroy helpers at logoff or explicit unlog. `afslogon.c` uses this contract to choose between KFW and legacy `ka_UserAuthenticateGeneral2`.

## State And Persistence
No storage is declared here, but the API implies three persistent surfaces: registry-configured KFW behavior, Kerberos ccaches including LSA and FILE caches, and installed AFS tokens. The cache copy helpers indicate cross-logon-session movement of credential files with Windows ACL protection.

## Dependencies, Risks, And Test Signals
Because the header exposes Windows types such as `BOOL`, `DWORD`, and `HANDLE`, it is Windows-only and must be included after suitable platform headers in consumers. Risks are mainly ABI drift: declarations here must match `afskfw.c` and any delayed Kerberos compatibility signatures. Test signals are compile coverage for all consumers, integrated logon using `KFW_AFS_get_cred`, logoff cleanup via destroy helpers, LSA principal lookup, and file ccache copy behavior under restricted user tokens.
