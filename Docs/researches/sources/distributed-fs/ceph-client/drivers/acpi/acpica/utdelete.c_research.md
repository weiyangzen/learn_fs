# sources/distributed-fs/ceph-client/drivers/acpi/acpica/utdelete.c

Purpose: `utdelete.c` owns internal ACPI operand-object reference counting and destruction. It releases type-specific resources, walks subobject graphs, prevents recursive package deletion stack growth, and deletes objects when reference counts reach zero.

Important APIs/types/functions: Public helpers are `acpi_ut_delete_internal_object_list()`, `acpi_ut_update_object_reference()`, `acpi_ut_add_reference()`, and `acpi_ut_remove_reference()`. Static `acpi_ut_update_ref_count()` updates one object's count under `acpi_gbl_reference_count_lock`; static `acpi_ut_delete_internal_obj()` frees type-specific resources and object descriptors.

Control flow: Refcount updates validate objects, skip namespace nodes where appropriate, update subobjects before the parent, and use a generic-state stack to avoid recursion through complex packages. Type-specific deletion frees strings/buffers/packages, GPE blocks, notify/address handlers, global-lock resources, OS mutexes/semaphores, method mutexes, region address ranges and handler contexts, secondary objects, PCC buffers, and address-handler mutexes. `REF_DECREMENT` deletes the object only when the new count is zero.

State and persistence behavior: The file mutates `common.reference_count`, global lock globals, address-range lists, handler region lists, GPE blocks, notify handler references, and object cache/descriptors. Deletion is permanent and releases memory/OS resources.

Dependencies and integration points: It depends on interpreter mutex unlinking, namespace secondary-object helpers, event/GPE deletion, address range removal, allocation/cache deletion, OS synchronization primitives, and object validation. It is used throughout namespace detach, method return cleanup, argument cleanup, table unload, and subsystem shutdown.

Risks and test signals: This is a high-risk lifecycle file. Risks include refcount underflow/overflow, circular region handler lists, deleting static table-backed buffers/strings, missed subobject references in packages/fields/references, global-lock special-case errors, and lock ordering around reference count updates. Tests should stress nested packages, bank/index/buffer fields, region handler detach, notify lists, global lock deletion, object list cleanup, invalid object guards, and leak/refcount accounting under repeated table load/unload.
