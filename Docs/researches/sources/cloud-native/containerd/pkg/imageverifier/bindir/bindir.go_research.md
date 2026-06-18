<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/imageverifier/bindir/bindir.go -->
# sources/cloud-native/containerd/pkg/imageverifier/bindir/bindir.go

Purpose: image verifier implementation that runs executable verifier binaries from a configured directory and combines their judgements.

Important APIs and types: `Config`, `ImageVerifier`, `NewImageVerifier`, `VerifyImage`, `runVerifier`, and `outputLimitBytes`. It implements `imageverifier.ImageVerifier`.

Control flow and state: `VerifyImage` reads verifier directory entries in sorted order, accepts images if the directory is missing/empty, enforces `MaxVerifiers`, and runs each verifier. A nonzero verifier exit code rejects the image with captured stdout reason; execution errors abort verification. `runVerifier` creates a timeout context, starts the binary with image name/digest/media-type args, writes the OCI descriptor JSON to stdin asynchronously, reads bounded stdout as the reason, logs bounded stderr line-by-line, drains truncated streams, waits for process exit, and returns exit code/reason.

Dependencies and integration: depends on `internal/tomlext` for duration config, `pkg/imageverifier` judgement types, containerd logging, OCI descriptors, and OS process/pipe primitives. Platform-specific process cleanup is supplied by sibling files outside this assignment.

Risks and test signals: this code executes external binaries, so timeout, pipe draining, output bounds, sorted order, and process cleanup are critical. Output is capped at 32 KiB and may be truncated. Directory contents are trusted as executables; deployment must control `BinDir`.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/imageverifier/bindir/bindir.go -->
