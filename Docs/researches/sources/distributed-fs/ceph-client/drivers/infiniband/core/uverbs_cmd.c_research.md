# sources/distributed-fs/ceph-client/drivers/infiniband/core/uverbs_cmd.c

## Purpose

`uverbs_cmd.c` implements the legacy write and write_ex userspace verbs command surface for RDMA devices. It translates `ib_user_verbs` ABI requests into RDMA core/provider operations, manages uobject allocation and lookup, copies responses with ABI extension semantics, creates and destroys core verbs objects, posts work requests, converts flow specifications, and registers the write-command interface in `uverbs_def_write_intf`.

## Important APIs, Types, and Functions

- Request/response helpers: `uverbs_request`, `uverbs_response`, `uverbs_response_length`, `uverbs_request_start/next/finish`, and `uverbs_get_cleared_udata`.
- Context and device commands: `ib_alloc_ucontext`, `ib_init_ucontext`, `ib_uverbs_get_context`, `ib_uverbs_query_device`, `ib_uverbs_ex_query_device`, and `ib_uverbs_query_port`.
- Object management commands cover PD, XRCD, MR, MW, completion channels, CQ, QP, AH, multicast attach/detach, WQ, RWQ indirection tables, flows, and SRQ.
- Work posting functions are `ib_uverbs_post_send`, `ib_uverbs_post_recv`, `ib_uverbs_post_srq_recv`, with receive marshalling in `ib_uverbs_unmarshall_recv`.
- Flow conversion helpers include `flow_resources_alloc`, `flow_resources_add`, `ib_uverbs_flow_resources_free`, `kern_spec_to_ib_spec_action`, and `ib_uverbs_kern_spec_to_ib_spec_filter`.
- `uverbs_def_write_intf` is the authoritative table mapping legacy command numbers to handlers, expected request/response sizes, required provider ops, and object categories.

## Control Flow

Handlers follow a repeated pattern. They copy a fixed or iterator-based request from userspace, validate ABI fields, allocate or look up uobjects, translate user handles to kernel RDMA objects, call provider or core RDMA operations with `attrs->driver_udata`, fill response structures, copy responses back, and finalize or abort uobjects. `uverbs_response` intentionally truncates to smaller user buffers and zero-fills larger ones to support ABI extension.

Context creation allocates an `ib_ucontext`, allocates an async event uobject, returns the async fd and completion vector count, calls the provider `alloc_ucontext`, charges rdmacg, adds restrack state, and publishes `file->ucontext` with release ordering. Query commands copy device and port capabilities into legacy structs, including extended ODP, RSS, raw packet, tag matching, CQ moderation, and device-memory fields in the ex query path.

Resource creation is layered on uobjects. PD/MR/MW/CQ/QP/AH/SRQ/WQ/RWQ table handlers allocate the uobject first, obtain dependent objects with read locks, call provider constructors, initialize use counts/event handlers/restrack records, release dependencies, and finalize the uobject. Destroy handlers usually call `uobj_get_destroy` or `uobj_perform_destroy`, collect event counters when applicable, then respond. XRCD uses an rb-tree keyed by inode so multiple opens of the same fd can share an XRCD with use counts.

QP creation supports RC, UC, UD, raw packet, XRC initiator/target, driver QPs, optional SRQ, optional RWQ indirection table, source QPN with raw capability, and default async event files. QP modification validates port numbers, QP states, AV transitions, Q_Key privilege requirements, alternate path consistency, and extended rate-limit bits before calling `ib_modify_qp_with_udata`.

Posting send and receive work requests uses iterator parsing for flexible arrays. Send posting copies each user WR, allocates the matching kernel WR type, resolves AH handles for UD sends, copies SGEs, chains WRs, calls provider `post_send`, returns a 1-based bad-WR index on failure, then drops references and frees all temporary WRs. Receive posting performs analogous unmarshalling for QP or SRQ receives.

Flow creation requires raw capability, validates flags, port, QP type, spec count and sizes, converts user specs into kernel `ib_flow_attr` specs, tracks action/counter resources, calls provider `create_flow`, and attaches flow resources to the uobject.

## State and Persistence

All state is runtime uverbs object state bound to an open uverbs file and the provider device. Objects created here persist across syscalls until explicit destroy, file close, or device disassociation. State includes ucontext publication, rdmacg charges, restrack entries, uobject IDs, provider object use counts, event counters, multicast lists, XRCD inode table entries, CQ/WQ/QP/SRQ event-file references, flow action/counter use counts, and posted work in provider queues.

## Dependencies and Integration Points

This file depends on `rdma_core` uobject infrastructure, provider `ib_device->ops`, RDMA restrack, rdmacg, userspace ABI structs from `ib_user_verbs.h`, uverbs named ioctl/type infrastructure, safe copy helpers, Linux fd/inode handling for XRCD, and event helpers declared in `uverbs.h`. It is one of the main integration points between userspace RDMA libraries such as libibverbs and hardware provider drivers.

## Risks

The file is security-critical because it parses complex user-controlled binary structs and creates DMA-capable hardware objects. Risks include integer overflows in flexible-array sizes, stale object references during destroy/disassociate, inconsistent provider use counts, missing cleanup after copy-to-user failure, raw-packet and privileged Q_Key capability bypasses, malformed flow specs, QP state transition validation gaps, and WR marshalling bugs that leak AH references or produce incorrect bad-WR indexes. Error unwinds are long and object-specific; they need continuous review when provider APIs change. Legacy ABI truncation/zero-fill semantics are intentional and must not be broken.

## Test Signals

Signals include libibverbs smoke tests for context, PD, MR, CQ, QP, AH, SRQ, WQ, RWQ indirection table, flow, and XRCD lifecycles; ABI compatibility tests with smaller/larger response buffers; failure injection for every constructor after dependency acquisition; CQ polling and notification; QP state transition tests including AV/port mismatch cases; post-send/recv bad-WR indexes; raw-packet permission denial; Q_Key privileged handling; flow spec fuzzing; device hot-unplug/disassociation while objects are live; rdmacg/restrack accounting balance; and leak checks for uobjects, event-file references, and provider use counts.
