# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/rvu_npa.c

## Purpose

`rvu_npa.c` implements the RVU Admin Function side of the NPA block, the OcteonTX2/CN10K packet buffer allocator used by NIX and other RVU engines. It handles NPA admin queue initialization/submission, NPALF allocation/free, aura and pool hardware context memory, queue interrupt context memory, context enabled bitmaps, optional NDC context lockdown, and a hardware erratum recovery helper for locked NDC cachelines.

The file has no filesystem persistence. It persists operational state in hardware registers, NPA AQ context memory, NDC cache state, and software mirrors hanging off `struct rvu_pfvf`.

## Important APIs, Types, And Functions

- `npa_aq_init` initializes NPA AQ endianness, NDC caching policy, CN10K batch DMA cache-line count, allocates the AQ instruction/result rings through `rvu_aq_alloc`, and writes `NPA_AF_AQ_CFG`/`NPA_AF_AQ_BASE`.
- `npa_aq_enqueue_wait` writes one `struct npa_aq_inst_s` to the current AQ head, clears shared result memory, rings the AQ doorbell, polls completion, and invokes `rvu_ndc_fix_locked_cacheline` on context fault/lock/poison completion codes.
- `rvu_npa_aq_enq_inst` is the main AQ operation implementation for aura and pool contexts. It validates LF and context bounds, serializes on `aq->lock`, handles WRITE/INIT/READ/LOCK/UNLOCK/NOP, translates aura pool indexes to pool context IOVA on INIT, updates aura/pool enabled bitmaps, and copies READ results into the mailbox response.
- `rvu_mbox_handler_npa_aq_enq` exposes AQ operations to mailbox callers and optionally locks newly initialized contexts when `CONFIG_NDC_DIS_DYNAMIC_CACHING` is enabled.
- `npa_lf_hwctx_disable` and `rvu_mbox_handler_npa_hwctx_disable` walk enabled aura or pool bitmaps and clear enable bits through AQ WRITE operations.
- `npa_ctx_free` releases per-PF/VF aura, pool, aura bitmap, pool bitmap, and NPA qint qmem state.
- `rvu_mbox_handler_npa_lf_alloc` resets the NPALF, allocates aura/pool/qint qmem, configures LF context bases/caching/way masks, and returns stack-page and qint/cache-line hardware information.
- `rvu_mbox_handler_npa_lf_free` resets the NPALF and frees per-LF context memory.
- `rvu_npa_init` and `rvu_npa_freemem` initialize/free the global NPA AQ for the first NPA block.
- `rvu_npa_lf_teardown` disables all active pools and auras then frees the PF/VF context memory for FLR or higher-level teardown.
- `rvu_ndc_fix_locked_cacheline` clears an NDC erratum condition where metadata lines can become locked while invalid.

Important context types are `struct npa_aq_inst_s`, `struct npa_aq_res_s`, `struct npa_aq_enq_req/rsp`, `struct npa_aura_s`, `struct npa_pool_s`, `struct npa_lf_alloc_req/rsp`, and the per-function `struct rvu_pfvf` fields `aura_ctx`, `pool_ctx`, `npa_qints_ctx`, `aura_bmap`, `pool_bmap`, and `npalf`.

## Control Flow

Global init is minimal: `rvu_npa_init` locates the NPA block for PF_FUNC 0 and calls `npa_aq_init`; if no NPA block exists it returns success. AQ init programs endianness, configures NPA NDC bypass bits, adjusts CN10K batch control when applicable, allocates AQ memory with enough result space for a response plus context and mask payloads, and writes AQ base/config registers.

NPALF allocation enters through `rvu_mbox_handler_npa_lf_alloc`. It validates aura size and pool count, masks cache way partition bits, validates that the PF/VF has an attached NPALF, resets the LF, reads hardware context-size fields from `NPA_AF_CONST1`, allocates qmem for aura contexts, pool contexts, and qint contexts, allocates bitmaps used to remember enabled aura/pool contexts, programs LF aura size/caching/way mask and qint caching/base registers, and returns stack page pointer/byte fields plus qint/cache-line capabilities.

AQ operations enter through `rvu_npa_aq_enq_inst`. The function validates the requested aura id against the aura context qsize, verifies LF attachment, finds the hardware NPALF, prepares an AQ instruction, then uses the shared AQ result memory under `aq->lock`. WRITE copies the requested aura/pool context and write mask; INIT copies a new aura/pool context and rewrites aura `pool_addr` from a pool index to the DMA address of that pool context; READ/LOCK/UNLOCK/NOP require no context payload. After `npa_aq_enqueue_wait` succeeds, the function updates aura or pool enabled bitmaps based on INIT or masked WRITE enable changes and copies readback context into the response.

Free and teardown paths reset or disable before releasing memory. Explicit LF free validates the LF, resets it with `rvu_lf_reset`, and calls `npa_ctx_free`. Teardown first clears all enabled pool contexts, then all enabled aura contexts, using the bitmaps as a sparse active set, and finally frees context memory. The disable path keeps going after per-context AQ failures, logging each failed context and returning the last error.

The NDC erratum helper disables CAM read interval enable, polls busy bits to idle, then walks all NDC banks/lines and clears lock bit 60 when valid bit 63 is clear. It is skipped on CN20K where NDC is not applicable.

## State And Persistence Behavior

Per-function NPA state lives in `struct rvu_pfvf`: `npalf` attachment, qmem pointers for aura/pool/qint contexts, and enabled bitmaps for auras and pools. The bitmaps are not hardware truth; they are software mirrors maintained only by successful INIT/WRITE AQ operations and used for efficient disable during teardown.

Hardware-visible state includes LF context base registers, aura size/caching/way-mask configuration, qint base/config registers, AQ instruction/result memory, NPA aura and pool contexts, batch control, NDC caching mode, and NDC metadata lock bits. `qmem_alloc` provides DMA-addressable context memory and `qmem_free` releases it.

`npa_ctx_free` nulls all freed pointers after releasing them, which makes repeated cleanup paths safer. `rvu_npa_freemem` only frees the block-level AQ memory; per-LF context memory is owned by PF/VF lifecycle paths.

## Dependencies And Integration Points

The file depends on RVU core services from `rvu.h`: block lookup, LF lookup, PF/VF lookup, register access, polling, LF reset, AQ allocation/free, and qmem allocation/free. It uses NPA hardware definitions from `rvu_struct.h` and `rvu_reg.h`, and Linux primitives for spinlocks, memory barriers, delay/poll loops, and allocation.

Mailbox handlers are the main caller-facing API: PF/VF drivers allocate NPALFs, configure aura/pool contexts, disable contexts, and free NPALFs through mailbox requests. NIX LF allocation validates NPA PF_FUNC mappings in `rvu_nix.c`, so NPA state is a dependency of NIX packet I/O. NDC recovery is shared with NIX: `rvu_ndc_fix_locked_cacheline` is defined here but called from both NPA and NIX AQ error paths.

Hardware-family integration matters: CN20K skips NDC cleanup; CN10K and newer NPA batch control reports cache-line count; `CONFIG_NDC_DIS_DYNAMIC_CACHING` changes both NDC configuration and post-INIT context locking behavior.

## Risks And Edge Cases

- `rvu_npa_aq_enq_inst` validates `req->aura_id` against aura qsize before branching on context type. Pool operations therefore also depend on the aura id range unless pool-specific qsize checks later catch INIT pool address use. This is likely intentional because the field is reused as context index, but it is a boundary worth testing when pool count and aura count differ.
- Pool bitmap allocation uses `NPA_AURA_COUNT(req->aura_sz)` entries rather than `req->nr_pools`. If pool count can exceed aura count, pool bitmap updates/teardown may miss or overrun logical ownership; if hardware/API guarantees otherwise, that contract should be documented by tests.
- AQ result memory is shared per block and protected by a spinlock. Any future path that sleeps while holding `aq->lock` or bypasses the lock would corrupt AQ result handling.
- AQ timeout returns `-EBUSY` after roughly 1000 micro-delay iterations; callers generally convert this to broad mailbox errors, so diagnosis depends on logs and hardware compcodes.
- INIT of aura contexts rewrites `req->aura.pool_addr` in place from a pool index to a DMA address. Reusing the same request object after a failed or repeated call could surprise callers.
- Context disable depends on software bitmaps. If bitmaps drift from hardware state, teardown will leave enabled hardware contexts behind.
- `rvu_ndc_fix_locked_cacheline` scans every bank/line after stopping CAM reads. Incorrect bank/line field interpretation or failure to re-enable a disabled interval elsewhere could affect NDC behavior beyond the failed AQ.
- Several cleanup paths ignore absent NPA blocks or already-null state. That is useful for teardown idempotence but can hide missing init in tests unless assertions inspect returned capabilities/state.

## Test Signals

- Init/free tests should validate AQ allocation, AQ register programming, endianness bit behavior, CN10K batch cache-line programming/reporting, CN20K NDC skip, and no-NPA-block early success.
- LF allocation tests should cover invalid aura size, zero pools, way-mask truncation, missing NPALF attachment, LF reset failure, qmem allocation failure at each allocation stage, aura/pool/qint base register programming, returned stack page fields, qints, and CN10K cache-line count.
- AQ tests should cover aura and pool INIT/WRITE/READ/LOCK/UNLOCK/NOP, invalid op, invalid aura id, invalid aura pool index, masked enable transitions, bitmap set/clear behavior, readback copying, AQ timeout, non-good compcodes, and NDC erratum recovery.
- Teardown tests should create sparse enabled aura/pool bitmaps, verify only enabled contexts get disable writes, confirm errors are logged and propagated while remaining contexts are attempted, and ensure qmem pointers/bitmaps are nulled after free.
- Integration tests should allocate NPA before NIX, verify NIX rejects invalid NPA PF_FUNC mappings, run NPA teardown under FLR while NIX queues are disabled, and validate no stale aura/pool contexts remain in hardware after reset.
