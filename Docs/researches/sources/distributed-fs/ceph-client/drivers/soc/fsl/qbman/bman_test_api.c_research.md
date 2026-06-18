# sources/distributed-fs/ceph-client/drivers/soc/fsl/qbman/bman_test_api.c

Purpose: high-level BMan API self-test. It allocates a pool, releases synthetic buffers, reacquires them, and verifies that every released token is returned exactly once.

Important APIs and functions: `bman_test_api()` drives the test. `bufs_init()` initializes 93 synthetic buffer addresses. `bufs_cmp()` handles BMan revision 2.x 40-bit address masking. `bufs_confirm()` checks one-to-one matching between input and output arrays.

Control flow: the test creates a BMan pool, repeats three loops of releasing buffers in batches up to 8, acquiring them back in reverse output slots, checking empty-pool behavior, and confirming token equality. It frees the pool on success and warns on failure paths.

State and persistence: static `pool`, `bufs_in`, `bufs_out`, and `bufs_received` are module-global test state. The BMan pool is hardware/global state during test and is freed afterward.

Dependencies and integration: depends on public BMan APIs, private `bman_ip_rev` revision information, and the BMan portal infrastructure being initialized on the executing CPU.

Risks and test signals: risks include synthetic addresses colliding with revision-specific masking, running on a CPU without an affine portal, and leaving a pool allocated on failure. Test signals are start/finish logs, no WARNs from buffer match counts or acquire counts, and no pool leaks after module load.
