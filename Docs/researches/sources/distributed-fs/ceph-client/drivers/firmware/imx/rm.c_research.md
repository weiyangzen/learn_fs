# sources/distributed-fs/ceph-client/drivers/firmware/imx/rm.c

Purpose: Exposes i.MX SCU Resource Management RPC helpers for ownership checks and owner lookup.

Important APIs/types/functions: `imx_sc_rm_is_resource_owned()` sends `IMX_SC_RM_FUNC_IS_RESOURCE_OWNED` and returns the firmware boolean from `hdr->func`. `imx_sc_rm_get_resource_owner()` sends `IMX_SC_RM_FUNC_GET_RESOURCE_OWNER` and returns the partition number through `pt`.

Control flow: Both helpers fill packed SCU RM messages and invoke `imx_scu_call_rpc()` with a response. Ownership check intentionally ignores the return code because firmware encodes only 0/1 in the response field.

State and persistence behavior: Stateless. Reads SCU resource ownership state; does not mutate ownership.

Dependencies and integration points: Depends on SCU RPC core and `linux/firmware/imx/svc/rm.h`. Used by platform drivers that need to confirm partition access to SCU-managed resources.

Risks and test signals: Ignoring the transport return in `imx_sc_rm_is_resource_owned()` can hide IPC failures as false/garbage ownership if the response is invalid. Test owned/unowned resources, invalid resource IDs, and IPC failure injection.
