# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_reg.h

Purpose: defines the macro layer that maps per-ASIC register tables to DMUB MMIO read/write, field set/update, and field get operations.

Important APIs and control flow: `BASE`, `REG_OFFSET`, `FD_SHIFT`, and `FD_MASK` bridge generated register names to offsets and bit metadata. `REG`, `FD`, and `FN` look up offsets/shifts/masks in the active `REGS` table, while `REG_READ` and `REG_WRITE` call the host callbacks through `CTX`. `REG_SET`, `REG_SET_2`, `REG_SET_3`, and `REG_SET_4` call `dmub_reg_set()` with an initial value. `REG_UPDATE`, `REG_UPDATE_2`, `REG_UPDATE_3`, and `REG_UPDATE_4` call `dmub_reg_update()` for read-modify-write. `REG_GET` extracts a field through `dmub_reg_get()`.

State and persistence behavior: no state, but the macros depend on each `.c` file defining `BASE_INNER`, `CTX`, and `REGS` correctly. Runtime persistence is hardware register state.

Dependencies and integration points: includes `dmub_cmd.h` for command types and declares the three helper functions implemented in `dmub_reg.c`. Every DMUB ASIC file includes this header after setting up its register table model.

Risks and test signals: risks include macro context leakage if `CTX`/`REGS` are wrong, field names not present in the table, no status propagation from MMIO callbacks, and multi-field vararg misuse only detected at runtime. Test signals are compile-time expansion across all ASIC files, boot register traces matching generated offsets, and read-modify-write preserving adjacent fields.
