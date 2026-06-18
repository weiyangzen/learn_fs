# sources/distributed-fs/ipfs-kubo/core/coreiface/options/unixfs.go

## Purpose
Builds UnixFS add/list settings and derives the CID prefix used by UnixFS imports.

## Important APIs, Types, and Functions
Defines `Layout`, `BalancedLayout`, `TrickleLayout`, `UnixfsAddSettings`, `UnixfsLsSettings`, `UnixfsAddOptions`, `UnixfsLsOptions`, `Unixfs` namespace, and many add/list option methods including CID/hash/raw leaves, chunker, layout, pin, hash-only, events, no-copy, HAMT limits, metadata preservation, and empty-directory inclusion.

## Control Flow and State
Defaults are CID version auto, sha2-256, balanced layout, size-262144 chunker, no pin, no hash-only, no-copy off, raw leaves off unless CIDv1, and include empty dirs. Normalization enforces no-copy implies raw leaves, non-sha2 implies CIDv1, CIDv0 only with sha2-256, explicit mtime/mode disables preserve flags, and HAMT fanout must be a power of two from 8 to 1024.

## Dependencies and Integration Points
Depends on Boxo UnixFS importer helpers/io, merkledag CID prefix helpers, go-cid, multihash, os, and time. Used by CoreAPI UnixFS add/list implementations and tests.

## Risks and Test Signals
Risks include option order interactions, CID default changes, invalid mtime nanoseconds, no-copy/raw-leaf compatibility, HAMT fanout validation, and empty-directory default semantics. Tests cover fanout validation and extensive UnixFS add/get/list behavior in conformance tests.
