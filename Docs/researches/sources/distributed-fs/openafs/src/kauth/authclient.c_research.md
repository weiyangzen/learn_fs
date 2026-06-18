# sources/distributed-fs/openafs/src/kauth/authclient.c

Purpose: client-side convenience layer for locating Authentication Servers, creating RX/Ubik connections with the right security class, authenticating with a password-derived key, fetching service tickets, and changing passwords.

Important APIs and functions: `ka_ExplicitCell`, `ka_GetServers`, `ka_GetSecurity`, `ka_SingleServerConn`, `ka_AuthSpecificServersConn`, `ka_AuthServerConn`, `ka_Authenticate`, `ka_GetToken`, and `ka_ChangePassword`. Internal helpers include `myCellLookup`, `CheckTicketAnswer`, and `kawrap_ubik_Call`.

Control flow and state: module globals cache the client config dir, explicit/debug cell server lists, and flags. Server connection routines open CellServDB data, initialize RX, construct either null or rxkad security objects, create RX connections for one or many servers, then initialize a Ubik client. `ka_Authenticate` encrypts a request, tries v2/v1/old RPCs, decrypts the response, and validates challenge, ticket times, identities, lengths, and labels. `ka_GetToken` encrypts requested times with the auth token session key, calls current/old TGS RPCs, decrypts, validates, and fills a `ktc_token`.

Dependencies and integration: uses hcrypto DES, rx/rxkad, Ubik, cellconfig, token structs, kauth generated stubs, and global pthread lock macros. Admin tools and user utilities call these routines.

Risks: legacy DES/rxkad protocol handling is security-sensitive; response parsing uses packed buffers and length arithmetic; `oldkey` in `ka_ChangePassword` is unused; explicit/debug globals affect lookup process-wide. Test signals should include multi-server fallback, single-server ambiguity, old/new RPC compatibility, malformed ticket answers, password expiration extraction, and authenticated versus null security connections.
