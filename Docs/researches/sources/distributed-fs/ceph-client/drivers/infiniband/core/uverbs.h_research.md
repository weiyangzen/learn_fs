# sources/distributed-fs/ceph-client/drivers/infiniband/core/uverbs.h

## Purpose

`uverbs.h` is the internal header shared by the RDMA userspace verbs implementation. It defines uverbs device, file-adjacent event queue, event object, QP/CQ/SRQ/WQ/XRCD wrapper, flow-spec, and DMA-BUF file helper structures, plus prototypes and small inline helpers used by `uverbs_cmd.c`, event handling code, and object type implementations.

## Important APIs, Types, and Functions

- `ib_uverbs_init_udata` and `ib_uverbs_init_udata_buf_or_null` initialize driver-facing `struct ib_udata` pointers and lengths.
- `struct ib_uverbs_device` holds the userspace verbs cdev, RDMA device RCU pointer, devnum, completion/refcount, xrcd tree, SRCU for disassociation, open-file list, and parsed uverbs API.
- `struct ib_uverbs_event_queue` is the common async/completion queue: spinlock, closed flag, waitqueue, fasync queue, and event list.
- `struct ib_uverbs_async_event_file` and `struct ib_uverbs_completion_event_file` wrap event queues in uobjects.
- `struct ib_uverbs_dmabuf_file` tracks a user-visible DMA-BUF object, mmap entry, physical vector, provider, kref, completion, and revoked flag.
- `struct ib_uevent_object`, `ib_ucq_object`, `ib_uqp_object`, `ib_usrq_object`, `ib_uwq_object`, and `ib_uxrcd_object` embed `ib_uobject` and add event counters, multicast lists, completion lists, and XRCD references.
- `struct ib_uverbs_flow_spec` is a union of all legacy user flow-spec formats used by flow creation conversion.
- `make_port_cap_flags`, `ib_uverbs_get_async_event`, `copy_port_attr_to_resp`, and `ib_uverbs_dmabuf_done` are inline/prototype integration helpers.

## Control Flow

This header does not implement a full control flow by itself; it defines the object model used by the uverbs command dispatcher. A typical command allocates or looks up an `ib_uobject`, stores an RDMA core object in the wrapper declared here, links event queues if asynchronous events are possible, and finalizes the object. Event handlers declared here append `ib_uverbs_event` records into `ib_uverbs_event_queue`. Destroy commands read event counters from wrapper objects before calling uobject destroy/put helpers.

`ib_uverbs_get_async_event` shows the common optional-event-file flow: it attempts to get a user-supplied async event uobject from an attribute bundle; if the attribute is absent, it falls back to `attrs->ufile->default_async_file`; if a file is found, it takes a uobject reference before returning.

## State and Persistence

The header describes runtime state only. Important lifetime contracts are documented in comments: `ib_uverbs_device` has module and open-file references; `ib_uverbs_file` has VFS and event-file references; event queues have VFS references and additional references from contexts or CQs. The structures here preserve user-visible IDs, event counts, multicast attachments, XRCD sharing, and DMA-BUF revocation state across syscalls while a uverbs file is open.

## Dependencies and Integration Points

It includes Linux kref/idr/mutex/completion/cdev and RDMA core headers for verbs, UMEM, user ABI structs, standard uverbs object types, and named ioctl definitions. It is consumed by legacy write commands, ioctl paths, event code, mmap/DMA-BUF code, and object method definitions. The macros around `UVERBS_MODULE_NAME` integrate this module's named ioctl namespace with RDMA uverbs infrastructure.

## Risks

Because this header encodes lifetime and wrapper structure layouts, changes can break object destruction, event delivery, or ABI command handlers across multiple files. Event queue closing, async file fallback, CQ event reference counts, and XRCD reference counters are especially sensitive. `make_port_cap_flags` preserves a historical ABI quirk for IP-based GIDs; changing it would be user-visible. The DMA-BUF file helper has kref/completion semantics that must match revoke and close paths elsewhere.

## Test Signals

Compilation is a major signal because many files depend on exact structure names and prototypes. Runtime signals include async event file creation/defaulting, CQ completion event delivery and counter reporting, QP multicast attach/detach cleanup, XRCD shared reference counts, port capability query output, and DMA-BUF uverbs object revoke/close completion.
