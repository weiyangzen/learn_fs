# sources/distributed-fs/ipfs-kubo/core/commands/multibase.go

## Purpose

`multibase.go` implements `ipfs multibase` utility commands for encoding, decoding, transcoding, and listing multibase encodings. It is a repo-independent data transformation command useful for IPFS/IPNS/PubSub workflows that expose multibase strings.

## Important APIs, Types, and Functions

`MbaseCmd` registers `encode`, `decode`, `transcode`, and shared `basesCmd` from elsewhere. `mbaseEncodeCmd`, `mbaseDecodeCmd`, and `mbaseTranscodeCmd` use `github.com/multiformats/go-multibase`. `CreateCmdExtras(SetDoesNotUseRepo(true))` marks the root as not needing a repo.

## Control Flow

Each command parses body/file args, obtains a single file/stdin reader through `cmdenv.GetFileArg`, and reads all input into memory. `encode` resolves an encoder by name, encodes raw bytes, and emits a string reader. `decode` decodes the input string and emits a bytes reader. `transcode` resolves the target encoder, decodes the input, re-encodes bytes in the target base, and emits a string reader.

## State and Persistence Behavior

The commands are stateless and do not use or mutate the IPFS repo. They operate entirely in memory and stream the final reader to the command response.

## Dependencies and Integration Points

Dependencies include `go-ipfs-cmds`, Kubo `cmdenv`, `go-multibase`, and standard `io`/`bytes`/`strings`. The utility integrates with pubsub topic/data encoding and key signature output where multibase strings are exchanged with users.

## Risks and Test Signals

Reading entire inputs into memory is acceptable for small utility use but risky for very large files. Tests should cover default base64url encoding, named bases, invalid base names, invalid multibase inputs, stdin/file handling, preserving binary bytes across encode/decode/transcode, and repo-less execution. Whitespace/newline handling should be explicit because `mbase.Decode(string(encodedData))` receives the raw file contents.
