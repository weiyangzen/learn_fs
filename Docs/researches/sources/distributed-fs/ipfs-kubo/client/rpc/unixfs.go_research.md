# sources/distributed-fs/ipfs-kubo/client/rpc/unixfs.go

## Purpose
This file implements UnixFS add and directory listing over HTTP RPC.

## Important APIs, Types, And Functions
`UnixfsAPI` exposes `Add` and `Ls`. `addEvent` models streaming add events. `lsLink`, `lsObject`, and `lsOutput` model `ls` responses.

## Control Flow
`Add` maps coreiface options to `add` flags, builds a multipart directory with the supplied node, negotiates multipart path encoding by remote version, streams add events, forwards optional progress events, and returns the last event CID. `Ls` streams `ls` output, validates one object/link per event, maps UnixFS data types to file types, and sends `iface.DirEntry` values until EOF or context cancellation.

## State And Persistence Behavior
Add mutates the remote blockstore and optionally pins. Ls is read-only.

## Dependencies And Integration Points
It integrates Kubo `add`/`ls`, Boxo files and UnixFS types, multihash code names, CID parsing, and progress event channels.

## Risks And Test Signals
Risks include returning the last add event only, upload compatibility with older daemons, channel blocking on progress/listing outputs, and a likely bug returning `err` instead of `resp.Error` in `Ls`. Signals are CoreAPI UnixFS add/list tests.
