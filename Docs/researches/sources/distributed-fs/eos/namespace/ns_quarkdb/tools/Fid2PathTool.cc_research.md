# sources/distributed-fs/eos/namespace/ns_quarkdb/tools/Fid2PathTool.cc

## Purpose
`Fid2PathTool.cc` is a small CLI that converts an EOS file ID into its hexadecimal file ID and corresponding FST data path prefix form.

## Important APIs, Types, and Functions
The program uses `CLI::App` to require `--fid`, then calls `eos::common::FileId::Fid2Hex()` and `eos::common::FileId::FidPrefix2FullPath()`. It prints `id`, `fxid`, and `path` fields to standard output. Although it includes `qclient/QClient.hh`, the tool does not use QuarkDB.

## Control Flow
`main()` builds the CLI parser, parses arguments, converts the signed integer `fid` to a hex string, uses hard-coded prefix `/data/`, derives the full path, prints the three lines, and exits zero. CLI parse errors are delegated to `app.exit(e)`.

## State and Persistence Behavior
The tool is read-only and stateless. It does not inspect filesystem state or namespace metadata; the output is purely a deterministic transformation of the supplied ID.

## Dependencies and Integration Points
It integrates with the common EOS file ID encoding helpers used by FST path layout logic. Operators can use it for diagnostics when correlating namespace IDs with on-disk data paths.

## Risks and Edge Cases
The input type is `int64_t`, so negative values may be accepted by the CLI and passed into file-ID conversion unless `FileId` rejects or normalizes them internally. The `/data/` prefix is hard-coded, so deployments using another data root need to reinterpret output. The command description says "translate fids to FST paths", but it does not validate that the path exists.

## Test Signals
Useful tests would compare known fid-to-hex and fid-to-path conversions, parse-error behavior for missing `--fid`, and edge cases for zero, large, and negative IDs.
