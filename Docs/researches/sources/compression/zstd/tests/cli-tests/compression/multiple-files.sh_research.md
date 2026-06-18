# sources/compression/zstd/tests/cli-tests/compression/multiple-files.sh

## Purpose
This test verifies mixed file and stdin handling for compression and decompression over multiple operands.

## APIs, control flow, and integration
It creates `file1` and `file2`, compresses `./file1`, stdin (`-`), and `./file2` in one command, pipes stdout to `zstd -d`, and separately checks `file1.zst` and `file2.zst`. It then removes originals and tests `zstd -d ./file1.zst - file2.zst` with a compressed stdin stream, confirming reconstructed files and stdout behavior. A final `-c` decompression case emits all outputs to stdout.

## State, dependencies, risks, and test signals
State is scratch-local files and `.zst` side effects. The test depends on default output naming, stdin marker semantics, and correct ordering of streamed outputs. Risks include subtle changes to mixed operand policy or overwrite behavior. Pass output demonstrates file outputs are created when expected and concatenated stdout data remains decodable.
