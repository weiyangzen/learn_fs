# File Research: sources/block-storage/thin-provisioning-tools/src/copier/base.rs

Defines core block-copy abstractions used by cache writeback and thin migration/copy code.

Types:
- `Block = u64`.
- `CopyOp { src, dst }`.
- `CopyStats { nr_blocks, nr_copied, read_errors, write_errors }`.
- `CopyProgress` trait for progress updates during and after a copy batch.
- `Copier` trait with `copy(&mut self, ops, progress) -> CopyStats`.

Semantics:
- Copy operations are block-index based.
- Trait documentation expects callers to sort operations in useful order, such as by destination for spindle-friendly writes.
