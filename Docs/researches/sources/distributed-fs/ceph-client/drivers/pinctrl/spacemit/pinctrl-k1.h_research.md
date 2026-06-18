## `sources/distributed-fs/ceph-client/drivers/pinctrl/spacemit/pinctrl-k1.h`

Purpose: local header for SpacemiT K1/K3 pinctrl data construction. It defines IO type encoding, standard voltage constants, and the macro used to create per-pin table entries.

Important APIs/types/functions: `enum spacemit_pin_io_type` distinguishes no IO, fixed 1.8V, fixed 3.3V, and external voltage pins. `PIN_POWER_STATE_1V8` and `PIN_POWER_STATE_3V3` define DT voltage values. `K1_PIN_IO_TYPE`, `K1_PIN_CAP_IO_TYPE()`, and `K1_PIN_GET_IO_TYPE()` encode/decode IO type in pin flags. `K1_FUNC_PIN()` constructs entries containing pin ID, GPIO mux function, and encoded IO type.

Control flow: no runtime flow. The generated/static arrays in `pinctrl-k1.c` rely on these macros and constants to define behavior later used by mux and pinconf code.

State and persistence: no mutable state. The encoded flags become immutable per-pin metadata, and `gpiofunc` values are later written to hardware during GPIO request.

Dependencies and integration: includes Linux bitfield, device, lock, platform, and pinctrl headers. It is private to the SpacemiT driver. Risks include encoding only two bits for IO type, no compile-time validation of macro arguments, and sharing `PIN_POWER_STATE_*` names with other pinctrl families if headers are combined. Test signals include build coverage of all `K1_FUNC_PIN()` users, debug output showing correct IO type descriptions, and pinconf tests for fixed versus external IO behavior.
