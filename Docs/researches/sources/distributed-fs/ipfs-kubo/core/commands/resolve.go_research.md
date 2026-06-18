# sources/distributed-fs/ipfs-kubo/core/commands/resolve.go

Purpose: implements `ipfs resolve`, resolving IPNS, DNSLink, IPFS, and IPLD paths to immutable IPFS/IPLD targets while honoring recursive resolution and CID output encoding options.

Important APIs/types/functions: `ResolveCmd` is a `cmds.Command` with options `--recursive`, `--dht-record-count`, and `--dht-timeout`. It emits `name.ResolvedPath` and has a text encoder that prints the resolved path.

Control flow: the command gets a CoreAPI via `cmdenv.GetApi`. For non-recursive `/ipns/` names, it calls `api.Name().Resolve` with depth 1 and optional DHT record count/timeout, tolerating `namesys.ErrResolveRecursion` as a valid partial result. Other inputs choose a CID encoder from explicit global options or from the input path, parse with `cmdutils.PathOrCidPath`, resolve through `api.ResolvePath`, rebuild the path with the selected CID base, validates it with `path.NewPath`, and emits it.

State and persistence behavior: read-only. It may consult name-system caches, DHT/IPNS records, DNS, and block/path resolvers through CoreAPI, but it does not mutate repo state.

Dependencies and integration points: bridges CLI command parsing to CoreAPI `Name().Resolve` and `ResolvePath`. Uses `boxo/namesys` resolve options, `go-cidutil` encoders, and Kubo command environment helpers.

Risks: DHT timeout parsing rejects negative values but permits zero as no timeout. Non-recursive behavior is special-cased only for `/ipns/`; other mutable protocols are resolved through `ResolvePath`. Incorrect CID-base selection can alter output compatibility for scripts.

Test signals: no direct file-local tests; command-tree validation in `root_test.go` covers command schema. CoreAPI path behavior is covered by `coreapi/test/path_test.go`.
