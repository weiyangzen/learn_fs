<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/pads-imx8qm.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/pads-imx8qm.h

## Purpose

`pads-imx8qm.h` defines the i.MX8QM pad ID and mux-option binding constants. It is used by device trees to select SCU-managed pad functions for the larger i.MX8QM family.

## Important APIs, Types, and Functions

The header exports 945 definitions: 269 numeric pad IDs and 675 pad/function/mux tuples. Numeric IDs cover SIM, M40/M41 microcontroller pins, GPT, UART, SCU/PMIC/boot pins, LVDS, MIPI DSI/CSI, HDMI/eDP, USB, QSPI, PCIe, SATA, eMMC/USDHC, ENET, ESAI/SPDIF, and many GPIO/companion-control pads. Function macros follow `IMX8QM_<pad>_<domain>_<signal>  IMX8QM_<pad>  <mux>`, with domains such as DMA, LSIO, SCU, MIPI, LVDS, DC, HDMI, HSIO, CONN, VPU, and audio.

## Control Flow

The file has no runtime control flow. The preprocessor expands selected macros into pad and mux cells, which the i.MX SCU pinctrl driver/firmware uses when applying pinctrl states for devices.

## State and Persistence Behavior

No mutable state exists in the header. Device-tree pinctrl states persist the selected constants in the DTB. Runtime state is in SCU-managed pad configuration and may be affected by firmware resource partitioning and low-power transitions.

## Dependencies and Integration Points

The header has no includes. Integration points include i.MX8QM board DTSI files, NXP SCU pinctrl bindings, SCFW resource management, and consumer devices for display, media, storage, network, serial, and control interfaces. The two trailing `_PAD` entries for ENET companion controls expose non-signal pad controls.

## Risks and Edge Cases

The catalog is large and copy/paste-sensitive. Similar pad names exist across M40, M41, LVDS0/1, MIPI DSI0/1, CSI0/1, and ENET instances. A function macro can compile while selecting a different instance or mux mode than the board wiring. The LSIO GPIO alternative often uses mux 3, while other i.MX8 derivatives use different GPIO mux slots; blindly porting pinctrl states from QXP/DXL is risky. SCFW ownership and power domains can reject otherwise valid DTS selections.

## Test Signals

Validation should compile representative i.MX8QM DTBs, run `dtbs_check`, inspect boot logs for SCU pinctrl errors, compare pinctrl debugfs with expected pad names, and smoke test each enabled peripheral. Static consistency checks should verify all function macros reference known pad IDs, mux values match NXP tables, and companion-control `_PAD` definitions are not used as ordinary data lines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/pads-imx8qm.h -->
