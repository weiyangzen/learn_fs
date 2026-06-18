# sources/distributed-fs/ceph-client/include/dt-bindings/reset/delta,tn48m-reset.h

Purpose: `delta,tn48m-reset.h` is a Devicetree binding header for a reset-controller provider. It exports
numeric C preprocessor constants that DTS files and provider drivers share as the ABI for phandle
cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 6 `#define`s covering reset-controller IDs and
reset-line indexes. The main macro families are CPU_88F7040 (1), CPU_88F6820 (1), MAC_98DX3265 (1),
PHY_88E1680 (1), PHY_88E1512 (1), POE_RESET (1). Representative constants are `CPU_88F7040_RESET`,
`CPU_88F6820_RESET`, `MAC_98DX3265_RESET`, `PHY_88E1680_RESET`, `PHY_88E1512_RESET`, `POE_RESET`,
`CPU_88F7040_RESET`, `CPU_88F6820_RESET`, `MAC_98DX3265_RESET`, `PHY_88E1680_RESET`,
`PHY_88E1512_RESET`, `POE_RESET`. Function-like helpers are none. Value shape: literal numeric range
0..5 across 6 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_RESET_TN48M_H`; after preprocessing, DTS C-preprocessor users and C drivers see only
the constants and any packing helpers. Comment-delimited groups or observed macro clusters are
`CPU_88F7040 group`, `CPU_88F6820 group`, `MAC_98DX3265 group`, `PHY_88E1680 group`, `PHY_88E1512
group`, `POE_RESET group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are reset-controller providers and consumer
device nodes that pass reset IDs in `resets` phandles.

Local source signals: The file is 20 lines long. Notable source comments include `Delta TN48M CPLD GPIO driver`,
`_DT_BINDINGS_RESET_TN48M_H`. Example value clusters are CPU_88F7040: `CPU_88F7040_RESET=0`;
CPU_88F6820: `CPU_88F6820_RESET=1`; MAC_98DX3265: `MAC_98DX3265_RESET=2`; PHY_88E1680:
`PHY_88E1680_RESET=3`; PHY_88E1512: `PHY_88E1512_RESET=4`.

Risks and test signals: Primary risks are reset ID drift can assert the wrong hardware line or leave a dependent block
permanently held in reset. Pay special attention to exported symbols such as `CPU_88F7040_RESET`,
`CPU_88F6820_RESET`, `MAC_98DX3265_RESET`, `PHY_88E1680_RESET`, `PHY_88E1512_RESET`, `POE_RESET`.
Test signals include DTS compile checks, reset-controller probe, driver reset/deassert paths, and
peripheral reinitialization after module or runtime-PM cycles.
