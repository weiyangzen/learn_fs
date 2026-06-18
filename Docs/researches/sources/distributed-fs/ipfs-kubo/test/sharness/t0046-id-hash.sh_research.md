## sources/distributed-fs/ipfs-kubo/test/sharness/t0046-id-hash.sh

Purpose: tests identity multihash behavior for inline CIDs and identity-hash content.

Important control flow: fetches and pins a random identity hash, adds small content with inline identity hash, confirms content is not stored as a normal block but remains retrievable, verifies block removal is a no-op, tests `--inline` and `--inline --raw-leaves`, exercises size threshold behavior with a larger file, then repeats key operations after enabling filestore and `--nocopy`.

State and dependencies: mutates blockstore, pins, and filestore config. Depends on `ipfs add`, `cat`, `pin`, `block rm`, `repo` semantics, and known identity multihash formatting.

Risks: inline data is intentionally not persisted like normal blocks, so blockstore/pin assumptions are subtle. Test signal is retrievability without stored block presence and correct identity multihash CIDs.
