# sources/distributed-fs/coda/coda-src/partition/tests/createmany.c

Purpose: stress-style helper to create many synthetic inodes on a named test partition.

Flow: initializes local `vicetab`, expects directory and count arguments, finds the partition, then loops from 1 through count calling `icreate` with deterministic volume/vnode/unique/version values derived from the loop index.

Risks/test signals: useful for allocation/free-map behavior and scalability. It has unused variables and older include paths/API names. It exits on first failed `icreate` but does not verify headers or file contents.
