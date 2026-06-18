# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/spctrl/interface/ia_css_spctrl_comm.h

## Purpose

`ia_css_spctrl_comm.h` defines the shared host/SP communication ABI for scalar processor startup. It provides the SP software-state values and the packed-by-contract DMEM initialization descriptor that host code writes into SP DMEM before starting firmware.

## Important APIs, Types, and Functions

`ia_css_spctrl_sp_sw_state` enumerates firmware lifecycle states: `IA_CSS_SP_SW_TERMINATED`, `IA_CSS_SP_SW_INITIALIZED`, `IA_CSS_SP_SW_CONNECTED`, and `IA_CSS_SP_SW_RUNNING`. `struct ia_css_sp_init_dmem_cfg` carries the DDR address of staged firmware data plus SP DMEM addresses and sizes for the data and BSS segments, along with the target `sp_id`.

`SIZE_OF_IA_CSS_SP_INIT_DMEM_CFG_STRUCT` computes the ABI size from `SIZE_OF_IA_CSS_PTR`, four 32-bit fields, and `sizeof(sp_ID_t)`. A `static_assert` requires the C structure size to match that expected layout.

## Control Flow

`spctrl.c` fills this descriptor during `ia_css_spctrl_load_fw()` and writes it to SP DMEM in `ia_css_spctrl_start()`. Firmware running on the SP reads the descriptor to copy initialized data from DDR into DMEM and clear its BSS region. The state enum is used by host-side state queries and by firmware-visible state symbols to report startup progress.

## State and Persistence Behavior

The header is declarative and persists no state itself. Its structure is copied into SP DMEM for each start operation, making it transient hardware/firmware state. The state enum describes a firmware-owned software-state variable; host code reads that variable from SP DMEM when querying SP status.

## Dependencies and Integration Points

The ABI depends on `type_support.h`, `linux/build_bug.h`, `ia_css_ptr`, `sp_ID_t`, and `SIZE_OF_IA_CSS_PTR`. It is consumed by `ia_css_spctrl.h` and `runtime/spctrl/src/spctrl.c`, and must remain compatible with SP firmware generated for the AtomISP CSS runtime.

## Risks and Edge Cases

The explicit size assertion protects only total size, not field order semantics, endian expectations, or the SP compiler's view of `sp_ID_t`. Any change to pointer width, padding rules, or firmware-side structure definition can break startup. The state enum has no explicit storage width, so host and firmware must agree on how the software-state symbol is represented when read as a 32-bit value.

## Test Signals

Build-time assertions are the first signal. Additional checks should compare generated host and firmware ABI headers, verify `sizeof(struct ia_css_sp_init_dmem_cfg)` on 32-bit and 64-bit builds, run firmware startup with known data/BSS contents, and confirm state transitions from terminated through running can be read from SP DMEM.
