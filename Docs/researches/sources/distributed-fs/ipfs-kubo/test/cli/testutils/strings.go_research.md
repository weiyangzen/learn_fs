# sources/distributed-fs/ipfs-kubo/test/cli/testutils/strings.go

Purpose: common string, multiaddr, and parallel iteration helpers for CLI tests.

Important APIs and variables: `AlphabetEasy` and `AlphabetHard` provide character sets. `StrCat` concatenates strings and string slices while dropping empty strings. `PreviewStr` returns a 10-byte preview with ellipsis when truncated. `SplitLines` scans a string into lines. `URLStrToMultiaddr` converts a URL host to a TCP multiaddr. `ForEachPar` runs a function over a slice concurrently and waits.

Control flow: `StrCat` type-switches each arg and panics on unsupported types. `PreviewStr` uses byte slicing, not rune slicing. `URLStrToMultiaddr` parses URL and `netip.AddrPort`, converts to `net.TCPAddr`, then to multiaddr. `ForEachPar` uses a `sync.WaitGroup` and launches one goroutine per element.

State and persistence: no persistent state. `ForEachPar` has transient goroutines.

Dependencies and integration points: used widely for command argument composition, log-friendly previews, multiaddr conversion in HTTP routing tests, and parallel harness operations.

Risks and test signals: `PreviewStr` can split UTF-8 sequences because it slices bytes. `URLStrToMultiaddr` panics for hostnames without numeric IP:port. `ForEachPar` does not recover panics and has no concurrency limit, so callers should avoid very large slices.
