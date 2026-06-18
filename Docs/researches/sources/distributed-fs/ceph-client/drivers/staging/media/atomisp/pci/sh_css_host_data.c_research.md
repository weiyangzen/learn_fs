# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/sh_css_host_data.c

Purpose: `sh_css_host_data.c` is a tiny allocation wrapper for host-side byte buffers that are later copied into HMM/DDR parameter memory. It gives callers a uniform `struct ia_css_host_data` containing a 32-bit size and an address allocated with kernel virtual memory helpers.

Important APIs/types/functions: `ia_css_host_data_allocate(size_t size)` allocates the wrapper with `kmalloc_obj()`, stores `size` as `uint32_t`, and allocates `address` with `kvmalloc()`. `ia_css_host_data_free(struct ia_css_host_data *me)` releases `address` with `kvfree()`, nulls the pointer, and frees the wrapper.

Control flow and state: there is no global state. Allocation is two-stage and unwinds the wrapper if the payload allocation fails. Free is null-safe.

Dependencies and integration: it includes `ia_css_host_data.h` for the data structure and `sh_css_internal.h` for local allocation helpers/macros. `sh_css_params.c` uses this abstraction when converting FPN, shading, and morph tables into ISP memory layout before storing through `hmm_store()`.

Risks: `size_t` is truncated to `uint32_t` in `me->size`, which is acceptable only if all CSS host data buffers fit in 32 bits. Callers assume `address` is initialized and `size` matches the payload length; mismatches can produce partial or excessive HMM stores. The helper does not zero the payload.

Test signals: allocation failure injection should cover wrapper and payload failure. Parameter conversion tests should verify allocated `size` equals the bytes passed to `hmm_store()`, and large-size tests should guard against truncation if future callers can request buffers above 4 GiB.
