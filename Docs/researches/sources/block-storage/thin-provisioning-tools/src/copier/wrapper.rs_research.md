# File Research: sources/block-storage/thin-provisioning-tools/src/copier/wrapper.rs

This file implements `ThreadedCopier`, a small worker-thread wrapper around any `Copier`.

`ThreadedCopier::run()` consumes batches of `CopyOp` values from an `mpsc::Receiver`, runs the wrapped copier, and terminates with an error on the first reported read or write failure.

Important behavior:
- Runs copying in a spawned thread and returns a `JoinHandle<Result<()>>`.
- Converts copier errors into contextual `anyhow!("copy failed: ...")`.
- Treats nonempty `read_errors` or `write_errors` as fatal, reporting the first failed source or destination block.

Integration points:
- Used where higher-level code wants a copier worker that receives batches asynchronously.
- Relies on shared `CopyProgress`.

Risks and notes:
- Stops on the first failing batch rather than attempting recovery.
- Error reporting includes only the first failed block in each failure vector.
