# sources/distributed-fs/ceph-client/fs/afs/cm_security.c

## Purpose
`cm_security.c` handles cache-manager-side RxRPC security challenge responses, including RxKAD/RxGK responses and optional creation of YFS RxGK callback appdata/token material.

## Important APIs, types, and functions
Public functions are `afs_process_oob_queue()` and, under `CONFIG_RXGK`, `afs_create_token_key()`. Internal functions include `afs_respond_to_challenge()` and `afs_create_yfs_cm_token()`. Constants include `RXGK_SERVER_ENC_TOKEN`, `xdr_round_up()`, and `xdr_len_object()`.

## Control flow
The OOB worker dequeues RxRPC out-of-band messages, responds to challenges for FS/VL/YFS services, rejects unknown services or unsupported security classes, and delegates to rxkad/rxgk helpers. YFS RxGK challenges may lazily create per-server callback appdata: random callback key, encrypted token container, client/server UUIDs, capability vector, and Kerberos-encrypted token payload.

## State and persistence
Runtime state includes the AFS netns cache-manager token key, per-server `cm_rxgk_appdata`, and random callback keys. These are in-memory security artifacts and are not persistent.

## Dependencies and integration points
It depends on RxRPC OOB APIs, RxKAD/RxGK helpers, Linux keyrings, Kerberos crypto, server peer appdata, AFS/YFS service IDs, and net/server UUIDs.

## Risks and test signals
Risks include accepting unknown challenge contexts, appdata size/XDR padding mistakes, enctype mismatch, token-key absence, random-key handling, and races in lazy server appdata creation. Test signals include RxKAD and RxGK challenge paths, unsupported security rejection, YFS callback challenge with appdata creation, keyring allocation failure, enctype absence, crypto failure injection, and repeated concurrent challenges.
