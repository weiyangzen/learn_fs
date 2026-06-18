## sources/distributed-fs/ceph-client/drivers/usb/gadget/function/u_tcm.h

Purpose: declares option state for the USB TCM/storage target gadget function.

Important APIs and types:
- `struct f_tcm_opts` embeds `usb_function_instance`, optional dependent module pointer, dependency lock, readiness/attach flags, `has_dep`, and callbacks for TCM registration/unregistration.

Control flow and integration:
- Legacy gadgets can set `dependent` so target portal group creation increments a module refcount and dropping it decrements the refcount.
- New programmatic function registration must provide sensible register/unregister callbacks to probe/remove the composite layer.
- `ready` and `can_attach` gate whether a USB function can be bound to a gadget.

State and persistence:
- Per-instance in-memory state, plus module reference state for an optional dependent module.

Dependencies:
- USB composite framework and target core/TCM implementation outside this header.

Risks:
- Incorrect dependent module refcounting can unload storage target code while in use or pin it forever.
- Missing callbacks in programmatic use can leave the composite gadget unprobed or unremoved.
- `can_attach` and `ready` need synchronization through `dep_lock`.

Test signals:
- Create/drop TPGs with and without a dependent module and check module refcounts.
- Bind/unbind TCM function only after `ready`/`can_attach` are set and verify callbacks fire exactly once.
