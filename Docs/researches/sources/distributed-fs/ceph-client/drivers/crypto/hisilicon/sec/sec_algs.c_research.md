# sources/distributed-fs/ceph-client/drivers/crypto/hisilicon/sec/sec_algs.c

## Purpose
`sec_algs.c` registers and implements asynchronous skcipher algorithms for the legacy HiSilicon SEC platform accelerator. It maps Linux crypto requests into SEC block descriptors, splits large requests to the hardware limit, maps scatterlists to hardware SGL chains, handles IV chaining, queues descriptors through `sec_drv.c`, and completes requests back to the crypto API.

## Important APIs, types, and functions
The public functions for the rest of the driver are `sec_alg_callback()`, `sec_algs_register()`, and `sec_algs_unregister()`. Internal setup is centered on `sec_c_alg_cfgs`, `sec_alg_skcipher_init_template()`, `sec_alg_skcipher_setkey*()` variants, `sec_alg_alloc_and_calc_split_sizes()`, `sec_map_and_split_sg()`, `sec_alg_alloc_and_fill_el()`, `sec_send_request()`, `sec_skcipher_alg_callback()`, and `sec_alg_skcipher_crypto()`. The registered `skcipher_alg` table covers AES ECB/CBC/CTR/XTS, DES ECB/CBC, and 3DES ECB/CBC.

## Control flow
Algorithm registration is reference-counted by `active_devs` under `algs_lock`; only the first SEC device registers the skcipher table, and the last unregister removes it. Per transform, init allocates a hardware queue with `sec_queue_alloc_start_safe()` and optionally a software FIFO for chaining modes. Setkey verifies AES/DES/3DES/XTS keys, allocates coherent key memory, stores the key, and prepares a descriptor template.

For each encrypt/decrypt request, `sec_alg_skcipher_crypto()` computes 32 MiB split sizes, DMA maps source and optional destination scatterlists, uses `sg_split()` for per-descriptor segments, maps the IV if required, allocates `sec_request_el` descriptors with hardware SGL chains, and then atomically either queues all elements or backlogs the request. `sec_send_request()` sends directly when hardware/software queues are empty enough for ordering, otherwise it places elements in the queue FIFO. Completion enters through `sec_alg_callback()` and `sec_skcipher_alg_callback()`, checks error bits, updates CBC/CTR IV state, drains a software queued element or backlog item when possible, frees completed element resources, unmaps DMA on final element, and calls `skcipher_request_complete()`.

## State and persistence behavior
Per-transform state lives in `struct sec_alg_tfm_ctx`: selected cipher algorithm, coherent key buffer/DMA address, descriptor template, assigned `sec_queue`, mutex, auth buffer placeholder, and backlog list. Per-request state lives in `struct sec_request` and a list of `struct sec_request_el` subrequests. Coherent key and DMA mappings are explicitly freed on transform exit or completion. There is no persistent state outside runtime memory and hardware queues.

## Dependencies and integration points
The file depends on the Linux crypto skcipher API, AES/DES/XTS key validation helpers, DMA mapping, scatterlist splitting, DMA pools from `sec_drv.c`, and queue functions declared in `sec_drv.h`. It integrates upward with the crypto API via `crypto_register_skciphers()` and downward with hardware via `sec_queue_send()` and completion callbacks.

## Risks and edge cases
The code must preserve request atomicity: partial hardware queueing cannot be safely unwound, so it checks capacity before sending all elements. Chaining modes depend on serialized completion and software FIFO behavior; incorrect queue-empty checks can break CBC/CTR IV sequencing. DMA mapping and split-array cleanup has many error paths. A notable edge is `entry_sum_in_sgl = count % SEC_MAX_SGE_NUM`, which becomes zero for exact multiples and must match hardware expectations. DES ECB is explicitly noted as lacking known test vectors. Backlog completion uses `-EINPROGRESS` notification once a request leaves backlog.

## Test signals
Use crypto selftests and `tcrypt`/AF_ALG coverage for AES ECB/CBC/CTR/XTS, DES, and 3DES in in-place and split source/destination modes; request sizes below, at, and above 32 MiB; scatterlists requiring multiple hardware SGLs; backlog behavior with queue pressure; IV update checks for CBC decrypt/encrypt and CTR; DMA mapping fault injection; and unload/reload with multiple SEC devices to validate algorithm reference counting.
