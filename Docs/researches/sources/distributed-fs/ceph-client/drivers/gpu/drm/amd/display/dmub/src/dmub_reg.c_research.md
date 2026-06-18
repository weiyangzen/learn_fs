# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_reg.c

Purpose: implements generic DMUB register field set/update/get helpers used by all ASIC-specific DMUB hardware files.

Important APIs and control flow: `set_reg_field_value_masks()` composes a masked field value into an accumulator. `set_reg_field_values()` consumes the first field and remaining varargs triples of shift, mask, and value to build one combined value/mask pair. `dmub_reg_update()` reads the current register through `srv->funcs.reg_read`, applies the combined mask/value, and writes it back. `dmub_reg_set()` applies fields to an explicit initial register value and writes without a read. `dmub_reg_get()` reads a register and extracts one masked field.

State and persistence behavior: no persistent software state. It writes hardware registers through the service's host callbacks. Register updates are read-modify-write operations, so persistence depends on hardware accepting the write and no concurrent writer changing the same register between read and write.

Dependencies and integration points: depends on `dmub_reg.h`, `dmub_srv.h`, C varargs, `ASSERT`, and `struct dmub_srv_funcs` register callbacks. All `REG_SET_*`, `REG_UPDATE_*`, and `REG_GET` macro uses in DCN files flow through these helpers.

Risks and test signals: risks include unchecked `reg_read`/`reg_write` failures because callbacks have no status channel, read-modify-write races on shared registers, varargs type/order mistakes, truncating shifts to `uint8_t`, and no validation that field values fit their masks. Test signals include unit-style field packing/extraction checks, register traces showing unrelated bits preserved, and stress coverage where interrupt ack/update paths share registers with firmware or other host code.
