## sources/distributed-fs/ipfs-kubo/test/sharness/t0052-object-diff.sh

Purpose: tests `ipfs object diff` for identity, added, removed, nested, and changed links, with raw-leaves variants.

Important control flow: creates directory/file objects, captures CIDs, runs diff against self and expects empty output, then compares expected diff records for added links, verbose added links, removed links, nested additions, and changed links. Raw-leaves versions ensure DAG layout differences do not break diff semantics.

State and dependencies: creates DAGs through `ipfs add` and stores them in the test repo. Depends on object diff output format, raw leaf behavior, and deterministic CIDs.

Risks: exact diff output is a stable CLI contract; changing path or type markers breaks users and tests. Test signal is empty self-diff and exact expected diff lines for each mutation category.
