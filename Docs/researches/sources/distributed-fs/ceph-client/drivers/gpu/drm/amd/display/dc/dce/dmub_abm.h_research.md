# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dmub_abm.h

Purpose: declares the DMUB-backed ABM factory/destructor used by DC resource code.

Important APIs: `dmub_abm_create()` takes a DC context plus DCE ABM register, shift, and mask descriptors and returns a generic `struct abm *` when DMCUB support is present. `dmub_abm_destroy()` releases the allocated object and nulls the caller pointer.

Control flow role: this header hides the concrete `struct dce_abm` allocation behind the generic ABM interface. Callers include the header when they want a DMCUB implementation instead of older DMCU-backed ABM.

State and persistence: no state is owned by the header. The created object persists function pointers, context, and register descriptors; hardware/firmware store ABM runtime state.

Dependencies and integration: includes `abm.h` for the public interface and `dce_abm.h` for descriptor types. Integrates with `dmub_abm_lcd.h` indirectly through the implementation.

Risks and test signals: the prototypes require descriptor types to stay ABI-compatible with `dce_abm`. Test compile coverage should ensure all resource constructors pass valid tables. Runtime tests should cover create returning null on non-DMCUB systems and destroy nulling the pointer.
