# sources/distributed-fs/ceph-client/sound/pci/ctxfi/cthw20k1.h

Purpose: public factory header for the ctxfi 20K1 hardware backend.

Important APIs and types: declares `create_20k1_hw_obj(struct hw **rhw)` and `destroy_20k1_hw_obj(struct hw *hw)`, including `cthardware.h` for the shared `struct hw` definition.

Control flow and integration: `cthardware.c` calls these functions when `chip_type` or PCI device indicates a 20K1 card. Generic ATC code never directly uses 20K1 internals beyond this factory interface.

State and persistence: no state; exposes constructors for the backend object.

Risks and test signals: header/API mismatch with `cthw20k1.c` would break module build. Test by compiling `CONFIG_SND_CTXFI` and probing a 20K1 device.
