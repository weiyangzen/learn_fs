# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mei/internal.h

Purpose: Declares internal iwlmei network datapath helpers shared by the MEI module implementation.

Important APIs and functions: `iwl_mei_rx_filter()` classifies inbound SKBs against SAP out-of-band filters and reports whether packets should pass to CSME. `iwl_mei_add_data_to_ring()` records SKB data into an internal ring, with `cb_tx` indicating transmit-side callback context.

Control flow: Implementations in iwlmei source files use these helpers from RX handler and packet-copy paths. The header itself has no executable flow.

State and persistence: No state declared here, but functions interact with iwlmei packet rings and filter state owned by the module.

Dependencies and integration points: Includes Ethernet UAPI, netdevice types, and `sap.h` protocol definitions. Used by `net.o`/`main.o` inside the iwlmei module.

Risks: RX handler return values control whether user space sees packets. Filter decisions must match CSME SAP expectations. Ring insertion must respect SKB lifetime and context.

Test signals: DHCP/OOB filter matching, pass/drop decisions through RX handler, ring population from TX/RX paths, and builds against SAP structure changes.
