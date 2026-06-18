# sources/distributed-fs/ceph-client/include/dt-bindings/reset/bcm6368-reset.h

Purpose: `bcm6368-reset.h` is a Devicetree binding header for a reset-controller provider. It exports numeric
C preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 9 `#define`s covering reset-controller IDs and
reset-line indexes. The main macro families are BCM6368 (9). Representative constants are
`BCM6368_RST_SPI`, `BCM6368_RST_MPI`, `BCM6368_RST_IPSEC`, `BCM6368_RST_EPHY`, `BCM6368_RST_SAR`,
`BCM6368_RST_SWITCH`, `BCM6368_RST_USBD`, `BCM6368_RST_USBH`, `BCM6368_RST_MPI`,
`BCM6368_RST_IPSEC`, `BCM6368_RST_EPHY`, `BCM6368_RST_SAR`, `BCM6368_RST_SWITCH`,
`BCM6368_RST_USBD`, `BCM6368_RST_USBH`, `BCM6368_RST_PCM`. Function-like helpers are none. Value
shape: literal numeric range 0..13 across 9 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_RESET_BCM6368_H`; after preprocessing, DTS C-preprocessor users and C drivers see
only the constants and any packing helpers. Comment-delimited groups or observed macro clusters are
`BCM6368 group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are reset-controller providers and consumer
device nodes that pass reset IDs in `resets` phandles.

Local source signals: The file is 16 lines long. Notable source comments include `__DT_BINDINGS_RESET_BCM6368_H`. Example
value clusters are BCM6368: `BCM6368_RST_SPI=0`, `BCM6368_RST_MPI=3`, `BCM6368_RST_IPSEC=4`,
`BCM6368_RST_EPHY=6`.

Risks and test signals: Primary risks are reset ID drift can assert the wrong hardware line or leave a dependent block
permanently held in reset. Pay special attention to exported symbols such as `BCM6368_RST_SPI`,
`BCM6368_RST_MPI`, `BCM6368_RST_IPSEC`, `BCM6368_RST_EPHY`, `BCM6368_RST_SAR`, `BCM6368_RST_SWITCH`,
`BCM6368_RST_USBD`, `BCM6368_RST_USBH`. Test signals include DTS compile checks, reset-controller
probe, driver reset/deassert paths, and peripheral reinitialization after module or runtime-PM
cycles.
