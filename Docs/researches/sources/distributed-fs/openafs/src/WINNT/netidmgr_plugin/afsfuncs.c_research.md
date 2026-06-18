# sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/afsfuncs.c

## Purpose

`afsfuncs.c` contains the AFS token and service helper logic for the NetIDMgr AFS credential provider. It detects the OpenAFS client service, lists and deletes tokens, maps AFS tokens into NetIDMgr credentials, obtains new tokens through Kerberos 5, krb524, Kerberos 4, or extension providers, resolves cell configuration, maps cells to realms, reports AFS errors, controls the Windows service, and checks identity realm compatibility.

## Important APIs, types, and functions

Public functions are `afs_is_running`, `afs_unlog`, `afs_unlog_cred`, `afs_princ_to_string`, `afs_list_tokens`, `afs_find_token`, `afs_list_tokens_internal`, `afs_klog`, `GetServiceStatus`, `ServiceControl`, `afs_report_error`, and `afs_check_for_cell_realm_match`. Important static helpers include `afs_filter_by_cell`, `afs_filter_for_token`, `afs_filter_krb5_tkt`, `afs_filter_krb4_tkt`, `ViceIDToUsername`, `copy_realm_of_ticket`, `afs_realm_of_cell`, `afs_get_cellconfig`, and `afs_get_cellconfig_callback`.

## Control flow

Service checks begin with `AfsAvailable` and `GetServiceStatus` against `TRANSARCAFSDAEMON`. `afs_unlog` forgets all tokens when the service is running. `afs_unlog_cred` extracts the token server principal from a NetIDMgr credential, logs a human-readable name, and calls `ktc_ForgetToken`.

`afs_list_tokens` flushes the plugin credential set, calls `afs_list_tokens_internal`, collects the resulting AFS credentials into the root NetIDMgr set, and updates the tray icon as token list, service stopped, or service error. `afs_list_tokens_internal` loops through `ktc_ListTokens`/`ktc_GetToken`, converts client and server principals to display strings, derives the AFS cell from the server principal, and associates each token with a NetIDMgr identity using layered heuristics: an existing root AFS token for the same cell, a matching Kerberos 5 `afs/<cell>` or `afs@<cell>` ticket, a matching Kerberos 4 `afs.<cell>` or `afs@<cell>` ticket, extension resolver callbacks, a persisted cell-to-identity mapping under `csp_afscred/Cells`, and finally a newly created identity based on the token principal. It then creates an AFS credential, sets method, issue/expire times, client/server principals, cell, and location attributes, and adds it to `afs_credset`.

`afs_klog` is the token-acquisition path. It verifies the service, normalizes null/empty service/cell/realm strings, resolves cell configuration from registry, cell file, or DNS, computes default service/cell/realm names, and attempts built-in Kerberos methods unless a specific method excludes them. The Kerberos 5 path initializes a context and cache for the identity, gets the client realm, tries service principals in several forms (`service/cell@realm`, `service@realm`, client realm, cell realm, and referral fallback), removes expired matching credentials and retries, embeds a Kerberos 5 ticket directly into an AFS token when possible, compares against an existing identical token, builds the AFS client principal, optionally maps/registers the user through the protection server with `ViceIDToUsername`, and calls `ktc_SetToken`. When built with Kerberos 4 support, failure or explicit krb524/krb4 selection can convert credentials through krb524d or obtain Kerberos 4 service tickets and set a v4-style token. If built-in methods do not obtain credentials and automatic or extension method mode is allowed, it dispatches to `afs_ext_klog`.

Cell and realm support flows through `afs_get_cellconfig`, which gets the root cell, fills a caller-supplied empty cell with the local cell, searches registry, cell file, and DNS for servers, and records linked-cell information. `afs_realm_of_cell` asks Kerberos 5 for the host realm of the first cell server or falls back to uppercasing the server DNS suffix or cell name.

## State and persistence behavior

The file mutates the global NetIDMgr AFS credential set, token state inside the OpenAFS cache manager through `ktc_SetToken`/forget APIs, service state through the Service Control Manager, and optional protection-server registration state via `pr_CreateUser`. It reads persistent cell data from OpenAFS registry/cellservdb/DNS sources and reads persisted NetIDMgr cell-to-identity mappings from `csp_afscred`. `afs_realm_of_cell` returns a pointer to a static realm buffer, so each call overwrites prior results.

## Dependencies and integration points

Dependencies include OpenAFS client/token APIs (`ktc_*`, `cm_*`, protection server functions), Kerberos 5 APIs and Heimdal ticket decoding, optional Kerberos 4 and krb524 dynamic imports, NetIDMgr credential and identity APIs, NetIDMgr error reporting, Windows service APIs, Winsock address structures, and extension dispatch from `afsext.c`. `afsconfigdlg.c` calls the service helpers; new-credential code calls `afs_klog`; notification icon code reflects `afs_list_tokens` results.

## Risks and edge cases

The identity-association logic is heuristic and can attach externally acquired tokens to the wrong identity when multiple identities have tickets for the same cell. `afs_get_cellconfig_callback` increments `numServers` without checking the destination array capacity visible in this file. `afs_realm_of_cell` uses static storage and is not thread-safe. Some assignments use `if (rc = ...)`, intentionally but easy to misread. `ViceIDToUsername` can create users in foreign cells when `ALLOW_REGISTER` is enabled. Kerberos acquisition has many fallback paths and can silently move from stronger/specific methods to legacy or extension behavior depending on build flags and method selection. Service-handle cleanup calls `CloseServiceHandle` on possibly null handles, which Windows tolerates poorly depending on API expectations.

## Test signals

Important tests include service stopped/running paths, list-token behavior with no tokens and multiple cells, identity association through each heuristic tier, expired ticket removal/retry, direct Kerberos 5 token setting, krb524/krb4 fallback builds, extension fallback success/failure, linked-cell output, cell config from registry/file/DNS, realm fallback with referrals, token deletion, service start/stop error handling, and realm-match checks for identities. Integration tests should confirm NetIDMgr attributes, expiration times, icon state, and no credential handle leaks.
