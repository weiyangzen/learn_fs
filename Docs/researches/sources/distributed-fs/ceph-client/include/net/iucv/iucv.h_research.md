# sources/distributed-fs/ceph-client/include/net/iucv/iucv.h

Purpose: Declares the low-level s390 IUCV programming interface for registering handlers, establishing/quiescing/resuming/severing paths, and sending/receiving/replying/purging messages.

Important APIs/types/functions: Flags such as `IUCV_IPRMDATA`, `IUCV_IPQUSCE`, `IUCV_IPBUFLST`, `IUCV_IPPRTY`, `IUCV_IPANSLST`, `IUCV_IPSYNC`, and `IUCV_IPLOCAL` mirror CP function flags. `iucv_array` describes 31-bit address/length buffer lists. `iucv_path` stores path id, message limit, flags, private pointer, handler, and list node. `iucv_message` stores id, audit, class, tag, length, reply size, inline rmmsg, and flags. `iucv_handler` is the interrupt callback vector for path and message events. `iucv_interface` exports function pointers and bus/root device handles.

Control flow: Users register an `iucv_handler`; pending path interrupts are offered in registration order and accepted by calling `iucv_path_accept`. Connected paths receive complete, sever, quiesce, resume, message pending, and message complete callbacks. Message APIs support receive, reply, reject, send, send2way, and purge.

State and persistence: Runtime state lives in allocated `iucv_path` objects, handler path lists, IUCV device bus state, and CP-managed message/path ids. Inline allocation initializes message limit and flags; free is plain `kfree`.

Dependencies/integration: Depends on s390 DMA/address types, device model bus registration, debug support, kmalloc, and CP Programming Services semantics.

Risks: Positive return codes are CP-returned status rather than errno; callers must handle both. Callback order affects ownership of pending paths. Buffer-list flags require valid 31-bit DMA-addressable arrays. Test signals include handler registration/unregistration, path pending accept/reject ordering, quiesce/resume behavior, priority and synchronous sends, buffer-list receive/send, send2way reply completion, and purge audit propagation.
