# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_power_well.h

Purpose: declares the concrete display power-well data model, iteration helpers, lookup IDs, exported operation tables, and hardware helper APIs used by i915 display power management.

Important APIs, types, and functions: `for_each_power_well()` and reverse iteration traverse the allocated well array. `enum i915_power_well_id` assigns stable IDs for direct lookup of special wells such as VLV display/DPIO, HSW global, SKL MISC_IO/PW1/PW2/DC_off, ICL PW3, TGL TC_cold_off, and BXT/GLK/CHV DPIO wells. `struct i915_power_well_instance` names an instance, links a domain list, carries an ID, and stores platform-specific index/PHY/AUX metadata. `struct i915_power_well_desc` binds ops, instances, IRQ pipe mask, always-on/fuse/fixed-delay/TC-TBT flags, and enable timeout. `struct i915_power_well` is the runtime object with descriptor, domain mask, count, cached HW state, and instance index. The header declares well lookup/refcount/state helpers, CHV lane power-gating helpers, DC-state helpers, and all operation-table externs.

Control flow: mapping tables instantiate descriptors and instances declared by this header, the power-domain core iterates and refcounts `struct i915_power_well`, and the operation implementation dereferences instance metadata to program the correct hardware. Special init and suspend paths use direct IDs through `lookup_power_well()`.

State and persistence: the runtime well object persists for the display instance lifetime after map initialization. It stores software refcounts and cached state only; hardware persistence is in platform registers controlled by operation callbacks.

Dependencies and integration points: includes `intel_display_power.h` for domain masks and `intel_dpio_phy.h` for DPIO metadata. It is shared by map, core, and operation implementation files, and by display code that needs direct power-well state such as DC and CHV PHY management.

Risks: descriptor fields are compact bitfields and small integers, so new platforms must fit counts/timeouts or adjust types. Direct lookup IDs must remain unique and are only assigned to wells that callers bypass through the domain framework. `for_each_power_well_reverse()` assumes at least one well when used, so callers must respect no-display cases. Cached enabled state can be stale if hardware changes outside the framework.

Test signals: compiler/linker coverage for extern ops, runtime debug output listing names/refcounts/domains, warnings for missing IDs in `lookup_power_well()`, and debug PM verification of cached/refcount/HW state consistency.
