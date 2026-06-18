# sources/distributed-fs/openafs/src/aklog/klog.c

## Purpose
`klog.c` implements a Kerberos 5 based `klog` command that accepts a username/password, obtains initial Kerberos credentials, derives an AFS service credential, and stores an AFS token. It preserves compatibility with older klog options while using Kerberos 5 and rxkad, with optional rxk5 support behind `AFS_RXK5`.

## Important APIs, types, and functions
`main` registers command syntax with the OpenAFS `cmd` package. `CommandProc` performs almost all work. Helpers include `getpipepass`, `silent_errors`, `whoami`, and `k5_to_k4_name`. The code uses `afs_krb5_skip_ticket_wrapper` for 524-style encrypted-part extraction, `tkt_DeriveDesKey`, `ktc_SetToken`, optional `ktc_SetK5Token`, `afsconf_GetCellInfo`, `pr_SNameToId`, and Kerberos ccache/credential APIs.

## Control flow
`main` defines parameters such as `-principal`, `-password`, `-cell`, `-k`, `-pipe`, `-silent`, `-setpag`, `-tmp`, `-noprdb`, `-unwrap`, `-k5`, `-k4`, and `-insecure_des`, then dispatches to `CommandProc`. `CommandProc` wipes command-line arguments, initializes Kerberos, rx, error tables, and cell config, selects a realm from `-k` or host realm lookup, parses the user principal, reads a password from the option, stdin, or Kerberos prompter, gets initial credentials, writes them to either the default ccache or an in-memory ccache, requests an AFS service ticket, and stores a token. The rxkad path either stores the full Kerberos 5 ticket or, with `-unwrap`, stores only the encrypted ticket part.

## State and persistence
Persistent effects include optional writing of a Kerberos ticket cache via `-tmp` and storing AFS tokens through `ktc_SetToken`/`ktc_SetK5Token`, optionally in a new PAG. Sensitive password buffers and command-line password arguments are zeroed. Process-global state holds `k5context`, `tdir`, and saved argv/argc for scrubbing.

## Dependencies and integration points
The command sits between OpenAFS cmd parsing, Kerberos initial-credential APIs, rx initialization, `cellconfig`, PTS lookups, `ktc` token storage, rxkad token formats, and `skipwrap`. It integrates with optional rxk5 support when compiled.

## Risks
Password-in-argv support is inherently risky despite scrubbing. The `always_evil` default makes encrypted-part-only handling active unless build/runtime conditions override through the `evil` calculation, so compatibility assumptions are important. Fixed-size principal buffers can truncate names. The service-ticket fallback from `afs/<cell>` to `afs` is intentional but must be covered for realms where both exist. Error handling exits immediately through `KLOGEXIT`, finalizing rx.

## Test signals
Cover interactive, `-pipe`, and explicit-password flows; `-silent` error suppression; `-tmp` ccache writing and fallback to memory cache; realm override and host-realm discovery; `-noprdb`; `-setpag`; `-unwrap` with valid and malformed tickets; rxk5/rxkad selection in `AFS_RXK5` builds; and invalid cell/principal/password cases.
