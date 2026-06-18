# Research: sources/distributed-fs/ipfs-kubo/core/commands/bitswap.go

Purpose: Implements Bitswap diagnostic and compatibility commands.

Important APIs/types/functions: `BitswapCmd` with subcommands `stat`, `wantlist`, `ledger`, and deprecated `reprovide`. `showWantlistCmd`, `bitswapStatCmd`, and `ledgerCmd` are the active implementations.

Control flow, state, and persistence: Wantlist command requires an online node, optionally decodes a peer ID, emits that peer's wantlist or the local wantlist, and text-encodes sorted CIDs. Stat command requires online node, gets `nd.Bitswap.Stat()`, and text-encodes block/data counters, duplicate data, wantlist, and optionally peers with human-readable sizes. Ledger decodes a peer ID and emits Bitswap ledger receipt for that peer. Deprecated reprovide aliases routing reprovide. No persistent state is modified except the aliased reprovide command may announce providers.

Dependencies and integration points: Uses command environment node access, Boxo Bitswap/stat/server receipt, CID encoder/sorting, humanize, and libp2p peer decode. Tied to online node Bitswap service.

Risks and test signals: Commands fail offline. Wantlist for self vs peer depends on peer ID equality. Verbose stat may expose peer IDs. No direct tests in this subset; behavior depends on Bitswap implementation.
