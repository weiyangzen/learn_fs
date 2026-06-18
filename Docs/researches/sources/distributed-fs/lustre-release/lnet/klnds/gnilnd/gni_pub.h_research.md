# sources/distributed-fs/lustre-release/lnet/klnds/gnilnd/gni_pub.h

## Purpose

`gni_pub.h` is the public Gemini/Aries Network Interface contract vendored with Lustre's GNILND LNet driver. It is a shared kernel/user header: common handle types, constants, return codes, completion event helpers, memory registration flags, endpoint/datagram semantics, SMSG mailbox attributes, RDMA/FMA/AMO descriptors, error-event structures, job/resource metadata, and NIC statistic enums are visible to both sides, while the bottom half exposes separate user-space `GNI_*` and kernel-space `gni_*` function prototypes behind `#ifndef __KERNEL__` and `#ifdef __KERNEL__`.

Within this Lustre tree, `gnilnd.h` includes this file and the rest of `lnet/klnds/gnilnd` treats its types as the ABI boundary to Cray kGNI/uGNI. `gnilnd_api_wrap.h` wraps the kernel `gni_*` calls with failure injection and return-code policy, so most Lustre call sites do not call the raw prototypes directly.

## Important APIs, Types, And Constants

- Version and protection domain metadata: `GNI_MAJOR_REV`, `GNI_MINOR_REV`, `GNI_VERSION`, `GNI_VERSION_CHECK`, reserved PTAG/PKEY enums, `GNI_FIND_ALLOC_PTAG`, and `GNI_JOB_CREATE_COOKIE()` define compatibility and job isolation identifiers. Lustre's module parameters use `GNI_JOB_CREATE_COOKIE(GNI_PKEY_LND, 0)` for the LND pkey cookie.
- Opaque handles: `gni_nic_handle_t`, `gni_cdm_handle_t`, `gni_ep_handle_t`, `gni_cq_handle_t`, `gni_err_handle_t`, `gni_msgq_handle_t`, and `gni_ce_handle_t` hide NIC, communication-domain, endpoint, completion-queue, error-queue, message-queue, and collective-engine state owned by the GNI stack.
- Return and state enums: `gni_return_t` is the central result contract (`GNI_RC_SUCCESS`, `GNI_RC_NOT_DONE`, `GNI_RC_ERROR_RESOURCE`, `GNI_RC_TRANSACTION_ERROR`, etc.). `gni_post_state_t` models datagram progress (`PENDING`, `COMPLETED`, `ERROR`, `TIMEOUT`, `TERMINATED`, `REMOTE_DATA`); Lustre maps these in `kgnilnd_process_dgram()`.
- SMSG: `gni_smsg_attr_t` describes mailbox type, buffer, size, memory handle, mailbox offset, credits, and max message size. Constants include `GNI_SMSG_TYPE_MBOX_AUTO_RETRANSMIT`, `GNI_SMSG_ANY_TAG`, `GNI_SMSG_MAX_SIZE`, and `FMA_SMSG_MAX_RETRANS_DEFAULT`.
- Memory registration: `gni_mem_handle_t`, `gni_mem_segment_t`, `gni_mem_handle_attr_t`, and `GNI_MEM_*` flags describe registered memory, physical or segmented mappings, ordering behavior, shared/dedicated MDD handling, and external/GPU memory. GNILND uses these for FMA mailbox blocks, RDMA payload pages, and MDD hold buffers.
- Completion queues: `gni_cq_entry_t`, `gni_cq_mode_t`, `GNI_CQ_*` modes, `GNI_CQMODE_*` event flags, and CQ accessor macros/functions define polling, blocking, overrun, event-data, and status decoding. `GNI_CQ_EVENT_TYPE_*` distinguishes post, SMSG, DMAPP, and MSGQ events.
- Posts and data movement: `gni_post_descriptor_t` is the core RDMA/FMA/AMO/CQWrite/CE descriptor. It carries linked-list fields, `post_id`, `status`, type, CQ event mode, delivery mode, local/remote addresses, memory handles, length, RDMA flags, source CQ, sync-flag fields, AMO command and operands, CQ write value, and CE fields.
- Network/job/resource metadata: `gni_ntt_descriptor_t`, `gni_error_event_t`, `gni_job_limits_t`, `gni_nic_device_t`, `gni_dev_res_desc_t`, `gni_job_res_desc_t`, and `gni_statistic_t` expose NTT configuration, error subscription, ALPS-style job configuration, resource introspection, and NIC counters.
- User-only API set: `GNI_CdmCreate/Attach/Destroy`, endpoint datagram APIs, memory APIs, CQ APIs including vector wait/monitor and interrupts, SMSG and tagged SMSG, MSGQ, error subscription/waiting, version/device/resource queries, CE/VCE APIs, balanced injection APIs, and NIC stat APIs.
- Kernel-only API set: lower-case analogs used by GNILND: `gni_cdm_create`, `gni_cdm_attach`, `gni_ep_create/bind/unbind/destroy`, datagram post/test/probe/cancel, `gni_mem_register(_segments)`, `gni_mem_deregister`, `gni_mem_mdd_release`, `gni_cq_create/destroy/get_event`, `gni_post_rdma`, `gni_post_fma`, `gni_get_completed`, SMSG init/send/getnext/release, error queue APIs, quiesce callback/status, and `gni_get_errno`.

## Control Flow And Expected Usage

The API is organized around a strict resource lifecycle. A caller creates a communication domain with a PTAG/cookie, attaches it to a NIC to obtain local PE address and NIC handle, creates completion queues, creates endpoints against a source CQ, binds endpoints to remote PE and instance IDs, then enables one or more transport mechanisms.

Datagram connection setup uses `gni_ep_postdata_w_id()` or `gni_ep_postdata()`, polls or waits with `gni_ep_postdata_test_by_id()`/`gni_postdata_probe_by_id()` variants, and may cancel via `gni_ep_postdata_cancel_by_id()`. GNILND stores the datagram pointer as the ID, probes completed IDs, and interprets `gni_post_state_t` to decide whether to process a connection request, keep waiting, or clean up a timeout/cancel.

SMSG control messages require both peers to exchange `gni_smsg_attr_t` values, register mailbox memory, bind the endpoint, then call `gni_smsg_init()`. Sends are non-blocking FMA mailbox copies that may return `GNI_RC_NOT_DONE` when credits are exhausted. Receivers call `gni_smsg_getnext()` and must call `gni_smsg_release()` after copying or processing the current message.

RDMA/FMA payload movement fills a `gni_post_descriptor_t`, posts with `gni_post_rdma()` or `gni_post_fma()`, receives CQ events via `gni_cq_get_event()`, then resolves event-to-descriptor completion with `gni_get_completed()`. The descriptor and its memory handles must stay valid until completion is consumed.

Teardown reverses setup: drain outstanding posts/SMSG/datagrams, unbind/destroy endpoints, deregister or release memory handles, destroy CQs, release error subscriptions, and destroy the CDM. GNILND asserts these invariants in device teardown before destroying CQs and CDM handles.

## State And Persistence Behavior

This header itself stores no persistent state; it declares ABI structures and routines whose implementations live in the external GNI stack. The state it models is mostly hardware/driver-backed and handle-scoped:

- CDM/NIC state persists from create/attach until destroy and carries PTAG/cookie isolation, modes, and device association.
- Endpoint state transitions from unbound to bound, then possibly SMSG-initialized, with outstanding datagram and post queues tracked by the GNI stack and by GNILND's connection/dgram objects.
- Registered memory state persists in NIC-visible memory descriptors (`gni_mem_handle_t`) until deregistered or MDD-released. GNILND tracks counts such as mapped bytes, MDDs, held MDDs, and FMA mailbox blocks around these handles.
- Completion queue state is consumable: `gni_cq_get_event()` removes a CQ entry, while `gni_get_completed()` removes the corresponding completed descriptor from a post queue. CQ overruns indicate lost events and require error handling.
- Error event subscriptions own an event queue until `gni_release_errors()`. Kernel quiesce callbacks and `gni_get_errno()` expose transient driver state used during reset or error diagnosis.
- User API includes checkpoint/resume/idling operations (`GNI_CdmCheckpoint`, `GNI_CdmResume`, `GNI_EpIdle`, `GNI_MsgqIdle`) for process checkpoint safety; kernel GNILND mainly uses the lower-case quiesce status/callback path.

## Dependencies And Integration Points

The header depends on `stdint.h` for user builds and on kernel-provided integer/bit macros for kernel builds. Several constants assume Cray Gemini/Aries/Pisces GNI hardware semantics: PTAG/PKEY reservation, NTT, MDD/MRT/GART/IOMMU, FMA/BTE/DLA resources, CE/VCE collectives, routing modes, and balanced injection.

GNILND integration is direct:

- `gnilnd.h` includes `<gni_pub.h>` and embeds public types in device, peer, connection, mailbox, memory, and transaction structures.
- `gnilnd_api_wrap.h` centralizes raw kernel calls, injects `CFS_FAIL_GNI_*` failures, maps `gni_return_t` to strings, and decides which return codes are expected, recoverable, logged, or fatal.
- `gnilnd_conn.c` uses `gni_smsg_attr_t`, `gni_smsg_buff_size_needed()`, memory registration flags, datagram post states, and cancel/test/probe APIs during connection setup and teardown.
- `gnilnd.c` creates and destroys CDMs, CQs, error subscriptions, and registered memory buffers as device lifecycle state.
- `gnilnd_cb.c`, `gnilnd_tx.c`, and related files use `gni_post_descriptor_t`, memory handles, CQ entries, and `GNI_CQ_*` helpers for RDMA/FMA transfer scheduling and completion.
- Hardware-specific headers such as `gnilnd_aries.h` and `gnilnd_gemini.h` select delivery modes, version requirements, and memory-registration flags such as relaxed PI ordering.

## Risks And Edge Cases

- ABI sensitivity: this file is a public hardware/driver contract. Changing struct layouts, enum values, macro encodings, or prototype signatures can break kernel/user compatibility and hardware interaction.
- Dual API naming: user-space `GNI_*` and kernel-space `gni_*` APIs are similar but not identical. For example, kernel `gni_cq_create()` takes a `gni_cq_event_hndlr_f` and user event data, while user `GNI_CqCreate()` takes mode, callback, and context. Mixing assumptions across build modes is risky.
- Asynchronous lifetime hazards: post descriptors, mailbox buffers, memory handles, and endpoint handles must remain valid until CQ and completion processing has fully drained. Premature deregistration or endpoint destruction can surface as transaction errors or resource leaks.
- Credit/resource exhaustion is normal, not always fatal. `GNI_RC_NOT_DONE`, `GNI_RC_ERROR_RESOURCE`, and CQ overrun statuses are part of flow control and must be classified per call site.
- CQ overrun means event loss. GNILND wrappers assert `GNI_CQ_OVERRUN()` on `GNI_RC_ERROR_RESOURCE`, so malformed CQ handling can panic rather than degrade.
- Datagram cancellation is subtle. `GNI_POST_PENDING` after cancel can require another driver progress cycle before `GNI_POST_TERMINATED`; GNILND explicitly handles this for wildcard datagrams.
- Endianness and wire layout: GNILND swaps fields inside exchanged `gni_smsg_attr_t` values and memory handles, so any change to exchanged structs needs matching wire compatibility work.
- Memory flags encode platform behavior. Ordering (`STRICT_PI`, `RELAXED_PI`), physical-contiguous mappings, shared/dedicated MDDs, and IOMMU/GART/MRT modes can alter correctness, resource pressure, or performance on Gemini versus Aries.
- Some comments contain stale naming or typos (`gni_puh.h`, `RMDA`, `Endpoind`), so consumers should trust the declarations and existing wrappers over prose when there is conflict.

## Test Signals

- Build both kernel-conditioned and user-conditioned consumers, or at least compile GNILND with `__KERNEL__` so the lower-case prototypes, `gni_errno_t`, and CQ event handler signature are exercised.
- Run or inspect GNILND failure-injection paths for `CFS_FAIL_GNI_CDM_CREATE`, CQ create/destroy/get-event, endpoint bind/post/test/cancel, SMSG init/send/getnext/release, memory register/deregister/MDD release, error subscription, and quiesce registration.
- Connection tests should cover successful datagram exchange, wildcard datagram cancellation, timeout, terminated states, bad peer attributes, and byte-swapped `gni_smsg_attr_t` fields.
- SMSG tests should cover mailbox size calculation, credit exhaustion (`GNI_RC_NOT_DONE`), retransmit limit behavior, getnext/release ordering, and remote-event races where a CQ event arrives before `gni_smsg_getnext()` sees a message.
- RDMA/FMA tests should validate descriptor filling, local and remote CQ event modes, `gni_get_completed()` descriptor recovery, CQ overrun handling, transaction-error decoding, and memory deregistration only after completion.
- Resource lifecycle tests should assert zero mapped bytes/MDD counts and empty device queues before teardown, then verify CQs, error handles, and CDM handles are destroyed exactly once.
- Version/resource checks should validate `GNI_VERSION_CHECK()` expectations, device type handling, and job/PTAG/PKEY configuration for the target Gemini or Aries environment.
