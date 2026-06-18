# sources/cloud-native/moby/daemon/libnetwork/drivers/overlay/joinleave.go

Purpose: Implements Linux overlay endpoint join/leave and NetworkDB table event handling for peer discovery.

Important APIs and functions: `Join` validates ids, locks the network, checks secure-key/XFRM support, initializes the network/subnet sandbox, creates a veth pair, sets MTU and MAC, attaches one side to the overlay sandbox bridge, configures static routes for other subnets, sets container interface names, adds the local peer to peer DB, and publishes a `PeerRecord` through `JoinInfo.AddTableEntry`. `DecodeTableEntry` decodes peer records for display. `EventNotify` applies NetworkDB peer add/delete updates while ignoring local peers and no-op updates. `Leave` removes the local peer and decrements sandbox join state.

Control flow: network lock guards endpoint lookup, sandbox state, and peer DB changes. Event handling unmarshals previous and new values, filters local peers, then does differential delete/add.

State and persistence: no datastore. Mutates kernel veth, bridge, VXLAN, neighbor/FDB, XFRM/firewall state through downstream calls and updates in-memory network/peer state.

Dependencies and integration points: central integration with `driverapi.JoinInfo`, NetworkDB table watcher, `PeerRecord` protobuf, overlay peerdb, OSL sandbox, netlink, and encryption.

Risks: large partial-failure surface during join after sandbox/link creation. Secure networks fail if keys or XFRM family support are unavailable. Static-route error logs but does not fail join.

Test signals: no direct join tests in this subset; overlay registration and peer/proto support are covered separately.
