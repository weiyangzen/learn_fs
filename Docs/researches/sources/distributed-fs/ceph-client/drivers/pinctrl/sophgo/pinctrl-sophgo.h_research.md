## `sources/distributed-fs/ceph-client/drivers/pinctrl/sophgo/pinctrl-sophgo.h`

Purpose: central Sophgo pinctrl interface shared by all Sophgo SoC implementations. It defines generic pin table structures, SoC callback contracts, VDDIO callback contracts, runtime controller state, exported common helper prototypes, and the common probe entry point.

Important APIs/types/functions: `struct sophgo_pin` stores pin ID and flags. `struct sophgo_pin_mux_config` binds a pin pointer to a DT mux config value. `struct sophgo_cfg_ops` defines SoC hooks for initialization, pinmux validation, group validation, DT post-processing, pinconf computation, pinconf writes, and mux writes. `struct sophgo_vddio_cfg_ops` defines electrical conversion hooks. `struct sophgo_pinctrl_data` packages pin descriptors, raw pin data, power-domain names, ops, pin count, power-domain count, and element size. `struct sophgo_pinctrl` stores device, pinctrl descriptors, locks, and SoC private state.

Control flow: SoC platform drivers provide `sophgo_pinctrl_data`; `sophgo_pinctrl_probe()` consumes it and wires generic Linux pinctrl callbacks to SoC-specific behavior. DT parsing and runtime pinctrl requests call the declared common functions, which in turn invoke callback pointers when present.

State and persistence: this header defines but does not allocate state. `mutex` protects DT/group construction; `raw_spinlock_t` protects MMIO register updates. `priv_ctrl` is an opaque pointer owned by the selected SoC backend. `pinsize` is essential for table traversal.

Dependencies and integration: includes Linux device, mutex, platform, spinlock, and pinctrl core headers plus local `../core.h`. It is the contract between common Sophgo code and CV18xx/SG2042 families. Risks include callback pointer assumptions in common code, incomplete ops causing NULL dereferences if a SoC omits required callbacks, `pinsize` mismatch breaking `bsearch()`, and weak compile-time validation of `pindata` ordering. Test signals include build/link coverage for all exported ops, probe with every compatible, invalid pin lookup behavior, and pinconf/mux calls for SoCs with and without optional validation hooks.
