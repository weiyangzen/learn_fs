<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/phy/phy-cadence.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/phy/phy-cadence.h

Purpose: Cadence SERDES binding constants for spread-spectrum clocking and Torrent/Sierra reference/PLL selections.

Important APIs/types/functions: This header exports 9 DT-visible macros in the `phy` binding namespace. Main API surface: `CDNS_SERDES_*_SSC`, `CDNS_TORRENT_*REFCLK`, and `CDNS_SIERRA_*` values encode clocking topology choices. First exported macros: `CDNS_SERDES_NO_SSC`, `CDNS_SERDES_EXTERNAL_SSC`, `CDNS_SERDES_INTERNAL_SSC`, `CDNS_TORRENT_REFCLK_DRIVER`, `CDNS_TORRENT_DERIVED_REFCLK`, `CDNS_TORRENT_RECEIVED_REFCLK`, `CDNS_SIERRA_PLL_CMNLC`, `CDNS_SIERRA_PLL_CMNLC1`. Last exported macros: `CDNS_TORRENT_REFCLK_DRIVER`, `CDNS_TORRENT_DERIVED_REFCLK`, `CDNS_TORRENT_RECEIVED_REFCLK`, `CDNS_SIERRA_PLL_CMNLC`, `CDNS_SIERRA_PLL_CMNLC1`, `CDNS_SIERRA_DERIVED_REFCLK`. Function-like/helper macros: No function-like macros; all exported constants are direct numeric or bit-field values.

Control flow: There is no runtime C control flow. The only execution-like behavior is C preprocessor expansion: device trees include the header, symbolic macro names become integer cells or bit fields, and kernel drivers later parse those cells during probe or configuration. Include guards prevent duplicate definitions, and any helper macros perform arithmetic or bit packing at preprocessing time.

State and persistence behavior: The file stores no runtime state and performs no persistence. Its numeric values are persistent ABI between DTS sources, compiled DTBs, and kernel drivers, so changing an existing value changes the meaning of shipped device trees.

Dependencies: No local include dependency. It otherwise depends only on the C preprocessor and the Linux devicetree binding include path.

Integration points: Cadence Torrent and Sierra PHY drivers decode these DT constants during PLL/refclock setup. The source-tree integration point is `include/dt-bindings`, which is shared by DTS files, binding examples, and drivers that need symbolic constants.

Risks: The major risk is ABI drift: renumbering macros, changing packed-bit layouts, or reusing a value with different hardware meaning can silently misconfigure clocks, resets, memory clients, PHYs, pinmuxes, interrupts, or regulators. For function-like macros, arithmetic offset formulas must match the provider driver's register layout. For large pin-function tables, duplicate or wrong alternate-function numbers can compile cleanly but route pins to the wrong signal.

Test signals: Useful validation is mostly integration-oriented: run `dtbs_check` for schemas that reference this header, compile representative DTBs, and boot or probe hardware/emulators enough to verify the relevant provider driver decodes the expected numeric IDs. Static checks should confirm include guards, macro count/names, no accidental renumbering against upstream, and successful preprocessing of DTS files using the first and last macros listed above.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/phy/phy-cadence.h -->
