# sources/distributed-fs/ceph-client/drivers/net/dsa/hirschmann/hellcreek_hwtstamp.h

Purpose: this header defines Hellcreek timestamp register offsets, timestamp status bits, skb metadata access, TX timeout policy, and exported hardware timestamping functions used by the main Hellcreek DSA driver and PTP worker.

Important APIs, types, and functions: register constants cover RX/TX status and data registers for front ports 1 and 2. `PR_TS_STATUS_TS_AVAIL` and `PR_TS_STATUS_TS_LOST` decode timestamp status. `SKB_PTP_TYPE()` stores an unsigned PTP class in `skb->cb`. `TX_TSTAMP_TIMEOUT` limits TX polling to 40 ms. Prototypes expose hwtstamp set/get, TX/RX timestamp callbacks, ethtool timestamp info, PTP worker callback, setup, and free.

Control flow: `hellcreek.c` installs the prototypes in `hellcreek_ds_ops`, while `hellcreek_ptp.c` assigns `hellcreek_hwtstamp_work()` as `ptp_clock_info.do_aux_work`. `hellcreek_hwtstamp.c` uses the register constants and timeout during worker-driven timestamp completion.

State and persistence: this file stores no state. It defines how per-port hwtstamp state in `struct hellcreek_port_hwtstamp` interacts with hardware timestamp status/data registers and skb control metadata.

Dependencies and integration points: it includes DSA and `hellcreek.h`, and relies on PTP clock types through function signatures. It is the interface boundary between DSA hwtstamp operations and the Hellcreek PTP worker.

Risks: `skb->cb` ownership must not conflict with other consumers before the packet is reinjected. The register map only names two user ports, matching current platform data. Timeout selection affects whether delayed TX timestamps are delivered or discarded.

Test signals: compile/link coverage across Hellcreek objects, TX status available/lost handling, timeout behavior, RX skb control field preservation until worker execution, and correct register selection for ports 2 and 3.
