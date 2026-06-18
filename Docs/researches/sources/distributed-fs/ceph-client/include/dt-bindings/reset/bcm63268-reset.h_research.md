# sources/distributed-fs/ceph-client/include/dt-bindings/reset/bcm63268-reset.h

Purpose: `bcm63268-reset.h` is a Devicetree binding header for a reset-controller provider. It exports
numeric C preprocessor constants that DTS files and provider drivers share as the ABI for phandle
cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 22 `#define`s covering reset-controller IDs and
reset-line indexes. The main macro families are BCM63268 (22). Representative constants are
`BCM63268_RST_SPI`, `BCM63268_RST_IPSEC`, `BCM63268_RST_EPHY`, `BCM63268_RST_SAR`,
`BCM63268_RST_ENETSW`, `BCM63268_RST_USBS`, `BCM63268_RST_USBH`, `BCM63268_RST_PCM`, `...`,
`BCM63268_RST_WLAN_UBUS`, `BCM63268_RST_DECT`, `BCM63268_RST_FAP1`, `BCM63268_RST_PCIE_HARD`,
`BCM63268_RST_GPHY`, `BCM63268_TRST_SW`, `BCM63268_TRST_HW`, `BCM63268_TRST_POR`. Function-like
helpers are none. Value shape: literal numeric range 0..31 across 22 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_RESET_BCM63268_H`; after preprocessing, DTS C-preprocessor users and C drivers see
only the constants and any packing helpers. Comment-delimited groups or observed macro clusters are
`BCM63268 group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are reset-controller providers and consumer
device nodes that pass reset IDs in `resets` phandles.

Local source signals: The file is 30 lines long. Notable source comments include `__DT_BINDINGS_RESET_BCM63268_H`. Example
value clusters are BCM63268: `BCM63268_RST_SPI=0`, `BCM63268_RST_IPSEC=1`, `BCM63268_RST_EPHY=2`,
`BCM63268_RST_SAR=3`.

Risks and test signals: Primary risks are reset ID drift can assert the wrong hardware line or leave a dependent block
permanently held in reset. Pay special attention to exported symbols such as `BCM63268_RST_SPI`,
`BCM63268_RST_IPSEC`, `BCM63268_RST_EPHY`, `BCM63268_RST_SAR`, `BCM63268_RST_ENETSW`,
`BCM63268_RST_USBS`, `BCM63268_RST_USBH`, `BCM63268_RST_PCM`. Test signals include DTS compile
checks, reset-controller probe, driver reset/deassert paths, and peripheral reinitialization after
module or runtime-PM cycles.
