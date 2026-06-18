<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/qcomtee/mem_obj.c -->
# sources/distributed-fs/ceph-client/drivers/tee/qcomtee/mem_obj.c

## Purpose

`mem_obj.c` wraps generic TEE shared-memory handles as QTEE callback objects so secure world can map Linux memory through QTEE's object protocol. It represents a `tee_shm` as a memory object and reuses that same wrapper as the mapping object returned to QTEE.

## Important APIs, Types, and Functions

`struct qcomtee_mem_object` embeds `struct qcomtee_object`, stores the backing `tee_shm`, and caches page-aligned physical address and size. `is_qcomtee_memobj_object()` identifies this object class by comparing callback ops. `qcomtee_memobj_param_to_object()` converts a userspace OBJREF with `QCOMTEE_OBJREF_FLAG_MEM` into a retained `tee_shm` wrapper. `qcomtee_memobj_param_from_object()` converts the wrapper back to a shared-memory ID if it belongs to the same TEE context. `qcomtee_mem_object_map()` returns physical address, size, RW permission, and a retained mapping object.

## Control Flow

During parameter conversion, the object ID is resolved with `tee_shm_get_from_id()`, a callback object is initialized with a name like `tee-shm-%d`, and the wrapper is returned as an input object to QTEE. Secure world requests mapping indirectly through the primordial object, which calls `qcomtee_mem_object_map()`. Mapping takes another reference to the same wrapper, fills address/length/permission fields, and hands that object back to QTEE; unmap is represented by QTEE releasing the mapping object, which eventually calls `qcomtee_mem_object_release()`.

## State and Persistence Behavior

State is transient. The memory wrapper keeps a reference to `tee_shm` until the object kref reaches zero, at which point `tee_shm_put()` and `kfree()` run. There is no separate map table or persistent mapping state in this file; QTEE owns the lifecycle by retaining and releasing object references.

## Dependencies and Integration Points

This file depends on generic `tee_shm_get_from_id()`/`tee_shm_put()`, the qcomtee object callback API, Qualcomm SCM permission constants (`QCOM_SCM_PERM_RW`), and `primordial_obj.c` for the privileged map operation. It also depends on `tee_shm` exposing physical address and size fields populated by the selected shared-memory pool.

## Risks and Edge Cases

`qcomtee_mem_object_dispatch()` rejects all direct operations, intentionally forcing map through the primordial object to avoid user-forged memory objects. That security property depends on `primordial_obj.c` validating the object type before calling `qcomtee_mem_object_map()`; the current map helper itself assumes the input is a memory object and uses `container_of()`. `qcomtee_memobj_param_from_object()` drops the object reference when exposing the original shm ID, so callers must not reuse that wrapper afterward. The implementation maps the full `tee_shm` with RW permission and has no subrange or read-only controls.

## Test Signals

Test valid and invalid MEM OBJREF IDs, same-context and cross-context conversion back to OBJREF, map requests through the primordial object, release of mapping objects, `tee_shm` lifetime under repeated map/unmap, forged non-memory callback objects passed to map, and physical address/size/page-alignment assumptions for dynamic and reserved shared-memory pools.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/qcomtee/mem_obj.c -->
