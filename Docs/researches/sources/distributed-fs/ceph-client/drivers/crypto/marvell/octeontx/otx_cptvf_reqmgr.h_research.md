# sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx/otx_cptvf_reqmgr.h Research

## sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx/otx_cptvf_reqmgr.h

### Purpose
`otx_cptvf_reqmgr.h` defines the OcteonTX VF request-manager ABI between crypto algorithms, the VF device, and hardware instruction submission.

### Important APIs, Types, And Functions
Important constants cover SG limits, DMA mode, context source, instruction queue alignment, max request size, command timeout, coalescing defaults and bounds. Key types include `union otx_cpt_opcode_info`, `struct otx_cptvf_request`, `struct otx_cpt_buf_ptr`, `union otx_cpt_ctrl_info`, CPT instruction command word unions, `struct otx_cpt_iq_cmd`, `struct otx_cpt_sglist_component`, `struct otx_cpt_pending_entry`, `struct otx_cpt_pending_queue`, `struct otx_cpt_req_info`, and `struct otx_cpt_info_buffer`. It defines inline `do_request_cleanup()` and declares request submission/post-process APIs.

### Control Flow, State, And Persistence
Per-request state persists from algorithm formatting through hardware completion and callback cleanup. `otx_cpt_req_info` holds input/output buffer arrays, opcode parameters, request type, encryption/truncated-HMAC flags, and callback. `otx_cpt_info_buffer` records DMA addresses and timing used by completion processing. `do_request_cleanup()` unmaps the SG list buffer plus all input/output DMA mappings and frees sensitive info memory.

### Dependencies, Integration Points, Risks, And Test Signals
The header depends on Linux crypto, PCI, and OcteonTX hardware types. Risks include endian-sensitive command/control bitfields, fixed SG array limits, cleanup relying on `info->req` being set, and all users obeying max request size. Test signals include build coverage for callers, cleanup after successful and failed requests, SG limit validation, coalescing sysfs bounds, command timeout behavior, and SE/AE group selection in CPTR.
