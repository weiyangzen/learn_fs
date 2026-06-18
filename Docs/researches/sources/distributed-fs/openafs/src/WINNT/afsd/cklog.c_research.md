# sources/distributed-fs/openafs/src/WINNT/afsd/cklog.c

## Purpose
`cklog.c` implements a Windows command-line authentication utility equivalent to `klog` for obtaining AFS kaserver credentials. It parses username, password, cell, lifetime, and behavior flags, authenticates through `ka_UserAuthenticateGeneral`, and optionally supports legacy ticket-file output when not built for `AFS_KERBEROS_ENV`.

## Important APIs And Functions
The executable initializes Winsock, uses the OpenAFS `cmd` parser, and defines `CommandProc` as the command handler. Supported options are `-principal`, `-password`, `-cell`, `-servers` (reported unavailable), `-pipe`, `-silent`, `-lifetime`, `-setpag`, and `-tmp`; `-x` is obsolete/no-op. Helper functions are `getpipepass`, bounded `good_gets`, and `read_pw_string`, which disables console echo while reading a password.

## Control Flow
`main` creates syntax, registers options, dispatches, and exits with the command code. `CommandProc` clears command-line arguments to reduce password exposure, determines silent/pipe/setpag/tmp modes, initializes the local cell and ka library, parses explicit cell and principal values, falls back to `USERNAME` or `GetUserName`, copies and clears any password argument, parses lifetime in `hh[:mm[:ss]]`, reads the password from stdin or no-echo console when needed, calls `ka_UserAuthenticateGeneral`, clears the password buffer, and returns the authentication code.

## State And Persistence
The command changes process memory and obtains AFS authentication state through the ka/ktc stack; there is no direct registry or file persistence in the normal `AFS_KERBEROS_ENV` build. Command-line password and copied password buffers are zeroed. The `-tmp` ticket-file path is disabled under the current compile-time define.

## Dependencies, Risks, And Test Signals
Dependencies include Winsock, OpenAFS command parser, `kautils`, cell config, and Windows console APIs. Risks include legacy kaserver authentication, a declared but unused `-setpag` mode in this implementation, unsupported `-servers`, and password exposure windows before argument clearing. Test signals include principal parsing with instance/cell, long cell/password rejection, lifetime parsing boundaries, pipe and no-echo password reads, silent-mode error suppression, default username fallback, failed and successful ka authentication, and password buffer zeroing after auth.
