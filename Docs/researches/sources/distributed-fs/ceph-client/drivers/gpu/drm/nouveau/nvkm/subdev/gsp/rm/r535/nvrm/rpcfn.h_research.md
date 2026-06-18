# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/nvrm/rpcfn.h

Purpose: enumerates the R535 GSP/RM RPC function numbers used on the command queue. The list spans legacy RM calls, GSP-specific static/system info calls, allocation/control/free calls, channel and GR controls, UVM-related functions, and newer maintenance controls.

Important definitions: key entries used in this work item include `NV_VGPU_MSG_FUNCTION_GET_GSP_STATIC_INFO`, `UNLOADING_GUEST_DRIVER`, `UPDATE_BAR_PDE`, `CONTINUATION_RECORD`, `GSP_SET_SYSTEM_INFO`, `SET_REGISTRY`, `GSP_RM_CONTROL`, `GSP_RM_ALLOC`, `CTRL_GPU_PROMOTE_CTX`, `CTRL_VASPACE_COPY_SERVER_RESERVED_PDES`, `CTRL_MC_SERVICE_INTERRUPTS`, and `NUM_FUNCTIONS`. The macro-based `X(UNIT, RPC)` list can either define an enum or be reused by custom macro expansion.

Control flow and state: `rpc.c` writes these values into `nvfw_gsp_rpc.function`, detects continuation records for split messages, and matches replies by function. `gsp.c` and RM helper layers select function IDs for boot-time and runtime operations.

Dependencies and integration: paired with payload headers such as `alloc.h`, `ctrl.h`, `gsp.h`, `bar.h`, `fifo.h`, and `vmm.h`. The transport layer's split-RPC logic depends on `CONTINUATION_RECORD` being correct.

Risks and tests: function-number drift is catastrophic because payloads would be interpreted by the wrong firmware handler. Split RPCs specifically require correct continuation function IDs. Test signals are successful boot RPCs, RM alloc/control/free sequences, large payload transfers, and correct errno mapping for RPC status failures.
