# sources/distributed-fs/openafs/src/afs/afs_nfsclnt.c

## Purpose
`afs_nfsclnt.c` manages AFS identities for the NFS translator/exporter path. It maps remote NFS clients by host and uid/PAG into `nfsclientpag` exporter records, handles request credential transformation, optionally fetches remote credentials and sysnames through PAG callback RPCs, and garbage-collects translator entries.

## Important APIs, types, and functions
The file defines `nfs_exportops`, `afs_nfspags`, `afs_xnfspag`, `afs_nfsexported`, and `init_nfsexporter`. Key functions are `afs_nfsclient_init`, `afs_nfsclient_reqhandler`, `afs_GetNfsClientPag`, `afs_FindNfsClientPag`, `afs_PutNfsClientPag`, `afs_nfsclient_hold`, `afs_nfsclient_getcreds`, `afs_nfsclient_sysname`, `afs_nfsclient_GC`, `afs_nfsclient_checkhost`, `afs_nfsclient_gethost`, `afs_nfsclient_stats`, and AIX IA UTH hooks when enabled.

## Control flow
`afs_nfsclient_init` registers exporter operations with the kernel exporter layer once. Each NFS request enters `afs_nfsclient_reqhandler`, which verifies the exporter is enabled, extracts uid and any PAG from credentials, tags the credential as an NFS translator call, verifies claimed PAGs against known `unixuser` records, finds or creates a host/uid `nfsclientpag`, calls `setpag` as needed to install the local translator PAG, associates the exporter with the corresponding `unixuser`, optionally refreshes tokens through `afs_nfsclient_getcreds`, and returns the PAG and exporter pointer to the caller.

`afs_nfsclient_getcreds` creates an Rx connection to the remote host's PAG callback service, fetches sysnames if absent, fetches credential blobs, maps cell names to local cells, creates or updates `unixuser` token sets for each cell, marks tokens primary/valid, and resets user connections. `afs_nfsclient_sysname` sets or reports sysname lists and can apply changes to all PAGs for a host. `afs_nfsclient_GC` frees entries with no references after timeout, matching a specific PAG, or all entries on shutdown.

## State and persistence behavior
State is in memory: hash buckets of `nfsclientpag` structures keyed by host, uid, and PAG; reference counts; last-call timestamps; sysname strings; exporter stats; and links from `unixuser->exporter` back to translator entries. Tokens installed into `unixuser` records are runtime credentials and are cleared/freed through normal token lifecycle.

## Dependencies and integration points
This module is wired into Solaris/AIX NFS dispatchers, the exporter abstraction, PAG/group credential routines, `unixuser` token management, Rx, PAGCB RPCs, cell lookup, and pioctl `exportafs` state. It is excluded when `AFS_NONFSTRANS` is defined except for selected AIX IA UTH cases.

## Risks and edge cases
Security depends on rejecting stale or forged remote PAGs, treating translator reboot as invalidating old remote PAGs, and correctly handling `EXP_CLIPAGS` remote-PAG mode. Reference counts must match exporter/user holds or GC can free live entries. `afs_nfsclient_getcreds` handles secret ticket material and must zero or free rejected tokens. The AIX IA UTH block appears syntactically suspect in this snapshot, so platform build coverage matters.

## Test signals
Test NFS export disabled rejection, first request creating a translator PAG, subsequent request reusing it, invalid remote PAG fallback, remote-PAG mode, callback credential import for multiple cells, sysname propagation, GC by timeout/PAG/shutdown, and exporter reference balance.
