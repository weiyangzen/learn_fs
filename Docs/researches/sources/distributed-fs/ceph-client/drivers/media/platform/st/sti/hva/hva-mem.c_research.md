# sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/hva/hva-mem.c

Purpose: allocates and frees DMA buffers used by HVA codec backends for task descriptors, sequence/context data, and reference/reconstructed frames.

Important APIs and functions: `hva_mem_alloc` allocates a devm-managed `struct hva_buffer` plus write-combined DMA memory, fills metadata, logs, and returns the buffer pointer. `hva_mem_free` releases the DMA memory and frees the metadata object.

Control flow: codec open paths allocate private hardware buffers through `hva_mem_alloc`; codec close paths call `hva_mem_free` for each successful allocation.

State and persistence: allocated buffers persist for the lifetime of an encoder context. Metadata includes name, DMA physical address, CPU virtual address, and size. No global state exists.

Dependencies and integration points: depends on `hva.h` for `ctx_to_dev` and error counters, Linux devm and DMA allocation APIs, and `hva-mem.h`.

Risks: `hva_mem_free` assumes non-null valid metadata. Mixing devm allocation for metadata with explicit DMA free is correct only if close paths run before device teardown; double-free paths must be avoided. Write-combined memory favors hardware writes and may surprise CPU read-heavy code.

Test signals: H.264 open/close leak checks, allocation failure injection after each buffer allocation stage, DMA address range validation, and repeated multi-instance create/destroy cycles.
