# sources/cloud-native/buildkit/util/archutil/fixtures/exit.mips64le.s

## Purpose
Assembly fixture for the linux/mips64le archutil probe. It builds a tiny static program that exits successfully when executed under the target architecture.

## Important APIs, Types, And Functions
Package: `n/a`. Build tags: `none`. Key declarations observed in the file: `none exported locally`.

## Control Flow, State, And Persistence
The generator compresses the compiled fixture into the corresponding *_binary.go constant. Runtime control flow is just architecture-specific syscall exit code handling.

## Dependencies And Integration Points
Important dependencies/imports: `standard library or generated runtime only`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are assembler/toolchain portability and syscall-number correctness. Integration signal is whether archutil probes execute under binfmt/QEMU.
