# sources/distributed-fs/ceph-client/sound/pci/ctxfi/cthardware.c

Purpose: chip-neutral factory and bitfield helper implementation for ctxfi hardware objects.

Important APIs and types: `create_hw_obj` selects `create_20k1_hw_obj` or `create_20k2_hw_obj`, stores PCI/chip/model fields, and returns a `struct hw`. `destroy_hw_obj` dispatches by PCI device ID to the matching destructor. `get_field` and `set_field` extract/insert values into masked bitfields.

Control flow: ATC calls `create_hw_obj` during hardware initialization and later destroys it during cleanup. Resource managers and chip backends use `get_field/set_field` to manipulate register fields without open-coding shifts.

State and persistence: factory sets runtime object fields only. No persistent state.

Dependencies and integration: depends on `cthardware.h`, `cthw20k1.h`, `cthw20k2.h`, and Linux `WARN_ON`.

Risks and test signals: `destroy_hw_obj` switches on `hw->pci->device` while creation switches on `chip_type`; mismatch would leak or fail teardown. `get_field/set_field` warn and no-op on zero masks. Test both chip families, unknown chip failure, and bitfield helpers for low and high mask positions.
