## sources/distributed-fs/openafs/src/kauth/krb_tf.c

Purpose: `krb_tf.c` exports `krb_write_ticket_file`, a compatibility bridge that takes the caller's existing AFS ticket-granting token and writes a Kerberos v4-style ticket cache file. It exists so AFS authentication can interoperate with tools that expect the historical `/tmp/tkt<uid>` or `KRBTKFILE` ticket-file format.

Important APIs and control flow: the function validates the realm length, constructs a `krbtgt.<realm>` server principal, lowercases the cell realm for the token lookup, and calls `ktc_GetToken` to fetch the token plus client principal from the kernel/interim token cache. It chooses the output path from `KRBTKFILE` or `gettmpdir()/tkt<uid>`, opens it with mode `0700`, and writes the client name/instance header followed by service, instance, uppercase realm, session key, Kerberos lifetime byte expanded into an `int`, kvno, ticket length, raw ticket bytes, and issue date.

State and persistence: this is explicitly persistent local state: it truncates or creates a ticket cache file containing reusable authentication material. It does not fsync or atomically replace the file, so interrupted writes can leave a partial cache. It closes the descriptor on both success and write failure.

Dependencies and integration points: depends on `ktc_GetToken`, `time_to_life`, `lcstring`, `ucstring`, OpenAFS `ktc_principal`/`ktc_token`, and platform temp-directory helpers. The format is documented in the file comment as Kerberos-derived but with null-terminated strings and host-order scalar fields.

Risks: the code treats `fd <= 0` as open failure, so a valid descriptor 0 would be reported as an error. Ticket cache data is written in host byte order, which matches the historical local-file contract but is not portable across architectures. The cache contains secret material; permissions are restrictive, but path selection via `KRBTKFILE` can target arbitrary locations selected by the environment.

Test signals: no direct test is in this file. `manyklog.c` and `kauth/test/multiklog.c` expose `-tmp` flows that call this function after authentication, giving integration coverage when those tools are built and run against a live cell.
