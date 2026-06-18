# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mana/mr.c

## Purpose
`mr.c` implements MANA memory registration, DMA MRs, memory windows, device memory allocation, and DM-backed MR registration.

## Important APIs, Types, And Functions
`mana_ib_verbs_to_gdma_access_flags()` translates RDMA access flags to GDMA access bits. `mana_ib_reg_user_mr()` pins userspace memory, creates a DMA region, and creates a GVA or zero-based VA MR. `mana_ib_reg_user_mr_dmabuf()` pins a dmabuf umem and creates a GVA MR. `mana_ib_get_dma_mr()` creates a GPA DMA MR. `mana_ib_alloc_mw()` and `mana_ib_dealloc_mw()` create/destroy type 1 or type 2 memory windows. `mana_ib_alloc_dm()`, `mana_ib_dealloc_dm()`, and `mana_ib_reg_dm_mr()` manage device memory and DM MRs. `mana_ib_dereg_mr()` destroys firmware MR state and releases local memory.

## Control Flow
Registration validates access flags and rejects `dmah`, allocates a driver MR, obtains an umem, creates a DMA region using the IOVA or zero-offset helper, fills `gdma_create_mr_params`, and sends `GDMA_CREATE_MR`. On success firmware owns the DMA region lifecycle as part of the MR. Error paths destroy DMA regions, release umems, and free the MR. Deregistration sends `GDMA_DESTROY_MR`, releases the umem if present, then frees the wrapper.

## State And Persistence
`mana_ib_mr` stores the firmware MR handle, lkey/rkey in the embedded `ib_mr`, and optional `umem`. `mana_ib_mw` stores a memory-window handle and rkey. `mana_ib_dm` stores a device-memory handle. All state is runtime-only and backed by firmware handles.

## Dependencies And Integration Points
The file depends on RDMA umem and dmabuf APIs, GDMA MR/DM commands, DMA-region helpers in `main.c`, PD handles, and access flags exposed through RDMA core.

## Risks
`mana_ib_reg_user_mr_dmabuf()` returns `-EOPNOTSUPP` for invalid flags while normal MR registration returns `-EINVAL`, which may matter to userspace. DM MR allocation does not store a `mr_handle` differently from normal MRs but shares deregistration semantics. Firmware ownership of DMA regions after MR creation means local cleanup must not destroy successful regions. The valid flag mask includes remote atomic even though device atomic capability reports none in query_device.

## Test Signals
Test normal, zero-based, dmabuf, GPA DMA, MW type 1/2, DM allocation, DM MR registration, invalid flags, dmah rejection, umem pin failure, DMA-region failure, firmware create/destroy failure, and lkey/rkey propagation.
