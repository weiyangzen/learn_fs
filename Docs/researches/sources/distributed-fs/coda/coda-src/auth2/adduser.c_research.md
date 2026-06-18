# sources/distributed-fs/coda/coda-src/auth2/adduser.c

Purpose: Legacy batch utility intended to add auth users from a file containing user/password records.

Important APIs/functions: `main`, `AddNewUser`, `MakeString`, `NextField`, and `NextRecord`.

Control flow: Parses `-f filename authuserid authpasswd`, initializes RPC, binds to auth server, reads the whole input file into memory, walks records, splits UID/password fields, looks up each UID's Vice ID, and calls `AuthNewUser` with an encryption key derived from the password.

State and persistence: Reads a batch file and mutates auth server password/user state through RPC. Maintains only an RPC binding and heap buffer locally.

Dependencies and integration: Includes `auth2.h` and uses auth RPC calls, but the binding call signature appears older than current `auser.h` declarations in this subset.

Risks and test signals: Contains serious legacy issues: malformed `#endif __cplusplus` syntax comments, outdated `U_BindToServer` call shape, off-by-one NUL write `area + buff.st_size + 1`, possible NULL dereference when `NextField` fails, missing return in `NextRecord`, fixed 256-byte parsing limits, and unsafe `strcpy`/`strcat`. It likely needs compile verification before use.
