# sources/compression/zstd/tests/cli-tests/compression/window-resize.sh

## Purpose
This test stresses long-window resizing by compressing a large generated file with an explicit long window and no content size.

## APIs, control flow, and integration
It generates a 1 GiB `file`, compresses with `zstd --long=30 -1 --single-thread --no-content-size -f file`, then lists the resulting frame with `zstd -l -v file.zst`. It removes `file` and `file.zst` at the end to keep scratch usage bounded.

## State, dependencies, risks, and test signals
The test temporarily consumes substantial disk and CPU. It depends on 64-bit address space or sufficient memory and on the CLI listing path. The major risk is resource pressure in constrained CI. A pass indicates the compressor can resize/encode the large window and the list command can inspect it.
