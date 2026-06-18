<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/net/microchip-lan78xx.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/net/microchip-lan78xx.h

Purpose: Microchip LAN7800/LAN7850 embedded PHY LED mode binding constants.

Important APIs/types/functions: This header exports 13 DT-visible macros in the `net` binding namespace. Main API surface: `LAN78XX_*` values select link/activity combinations, duplex/collision, autoneg-fault, and forced LED off/on modes. First exported macros: `LAN78XX_LINK_ACTIVITY`, `LAN78XX_LINK_1000_ACTIVITY`, `LAN78XX_LINK_100_ACTIVITY`, `LAN78XX_LINK_10_ACTIVITY`, `LAN78XX_LINK_100_1000_ACTIVITY`, `LAN78XX_LINK_10_1000_ACTIVITY`, `LAN78XX_LINK_10_100_ACTIVITY`, `LAN78XX_DUPLEX_COLLISION`. Last exported macros: `LAN78XX_DUPLEX_COLLISION`, `LAN78XX_COLLISION`, `LAN78XX_ACTIVITY`, `LAN78XX_AUTONEG_FAULT`, `LAN78XX_FORCE_LED_OFF`, `LAN78XX_FORCE_LED_ON`. Function-like/helper macros: No function-like macros; all exported constants are direct numeric or bit-field values.

Control flow: There is no runtime C control flow. The only execution-like behavior is C preprocessor expansion: device trees include the header, symbolic macro names become integer cells or bit fields, and kernel drivers later parse those cells during probe or configuration. Include guards prevent duplicate definitions, and any helper macros perform arithmetic or bit packing at preprocessing time.

State and persistence behavior: The file stores no runtime state and performs no persistence. Its numeric values are persistent ABI between DTS sources, compiled DTBs, and kernel drivers, so changing an existing value changes the meaning of shipped device trees.

Dependencies: No local include dependency. It otherwise depends only on the C preprocessor and the Linux devicetree binding include path.

Integration points: The LAN78xx Ethernet driver applies these values to PHY LED configuration registers from DT. The source-tree integration point is `include/dt-bindings`, which is shared by DTS files, binding examples, and drivers that need symbolic constants.

Risks: The major risk is ABI drift: renumbering macros, changing packed-bit layouts, or reusing a value with different hardware meaning can silently misconfigure clocks, resets, memory clients, PHYs, pinmuxes, interrupts, or regulators. For function-like macros, arithmetic offset formulas must match the provider driver's register layout. For large pin-function tables, duplicate or wrong alternate-function numbers can compile cleanly but route pins to the wrong signal.

Test signals: Useful validation is mostly integration-oriented: run `dtbs_check` for schemas that reference this header, compile representative DTBs, and boot or probe hardware/emulators enough to verify the relevant provider driver decodes the expected numeric IDs. Static checks should confirm include guards, macro count/names, no accidental renumbering against upstream, and successful preprocessing of DTS files using the first and last macros listed above.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/net/microchip-lan78xx.h -->
