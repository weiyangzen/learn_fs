# sources/distributed-fs/openafs/src/ptserver/readpwd.c research

## Purpose
`readpwd.c` is a small import utility that reads a passwd-format file and creates Protection Server user entries with the passwd uid as the requested PT id.

## Important APIs, types, and functions
`main` parses `[-v] [-c cellname] passwdfile`, initializes libprot with localauth-style security through `pr_Initialize(2, AFSDIR_CLIENT_ETC_DIRPATH, cellname)`, opens the input file, extracts username and uid fields from colon-separated lines, and calls `pr_CreateUser`. It prints `pr_ErrorMsg` diagnostics on failures. A local `osi_audit` stub satisfies non-server linkage.

## Control flow, state, and persistence
For each line, the utility copies the substring before the first colon into `name`, skips to the uid field, copies it into a small `uid` buffer, converts it with `atoi`, and passes that id by pointer to `pr_CreateUser`. A nonzero id requests `SPR_INewEntry` behavior on the server side. Persistent state changes are remote user entries in the protection database.

## Dependencies and integration points
The file depends on OpenAFS config paths, Rx/XDR headers, `ptuser.h`, and `ptprototypes.h`. It exercises the same client initialization and create-user path used by `pts createuser -id`.

## Risks and test signals
The parser assumes valid passwd lines with enough colon fields and has fixed-size buffers, including an 8-byte uid string. It should be tested with malformed lines, long usernames, large uid values, duplicate users/ids, missing files, verbose mode, and explicit cell selection. Since all persistence is delegated to the ptserver, server-side validation still protects name legality and id conflicts, but the utility can fail unclearly on malformed local input.
