# sources/cloud-native/stargz-snapshotter/cmd/ctr-remote/commands/get-toc-digest.go

Purpose: Defines `ctr-remote images get-toc-digest`, a debugging utility that reads a layer from containerd content store and prints its TOC digest or formatted TOC.

Important API: `GetTOCDigestCommand`. Flags select zstd:chunked parsing and optional `--dump-toc`.

Control flow: The action validates a layer digest argument, creates a containerd client, opens the content blob as `ReaderAt`, reads the appropriate footer size, selects gzip or zstd:chunked decompressor, parses footer to locate TOC, defaults TOC size when omitted, parses TOC from a section reader, then prints either marshaled indented TOC JSON or digest string.

State and persistence: Read-only against the containerd content store. No local writes.

Dependencies and integration: Uses eStargz and zstdchunked decompressors, OpenContainers digest parsing, and containerd ctr client setup.

Risks: Assumes footer read starts at `ra.Size()-footerSize`; too-small blobs cause read errors. Dumped TOC is re-marshaled and may not match original digest, as documented in flag text.

Test signals: No direct tests in this subset; coverage would need sample gzip and zstd chunked layers.
