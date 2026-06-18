# sources/distributed-fs/openafs/src/tests/write2

Purpose: shell smoke test for overwriting an existing file and seeing the new contents through a subsequent read.

Important behavior: it writes `hopp` to `foo`, verifies the read-back, overwrites `foo` with `hej`, verifies again, then removes the file.

State/dependencies: state is only the relative file `foo`. Dependencies are standard shell utilities and the current directory's filesystem semantics. Integration point is the AFS client cache path for truncate-on-redirection followed by read-after-write.

Risks/test signals: like `write1`, it normalizes away the newline via command substitution and does not test binary content, append behavior, or concurrent readers. It is a concise signal for overwrite/truncate propagation in the test volume.
