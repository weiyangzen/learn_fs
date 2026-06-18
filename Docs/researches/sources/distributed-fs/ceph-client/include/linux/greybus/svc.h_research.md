<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/greybus/svc.h -->
# sources/distributed-fs/ceph-client/include/linux/greybus/svc.h

Purpose: This header defines the Greybus SVC object and APIs for switch/control-plane operations such as routing, connection creation, interface power, DME access, pwrmon, ping, and watchdog.

Important APIs/types/functions: CPort flags encode E2EFC, CSD_N, and CSV_N. `enum gb_svc_state` tracks reset, protocol-version, and hello phases. `enum gb_svc_watchdog_bite` selects reset or panic action. `struct gb_svc` embeds a device, host, SVC connection, state, device IDA, workqueue, Endo/AP IDs, protocol version, watchdog/action, debugfs, and pwrmon rails. APIs create/add/delete/put SVC, sample pwrmon, assign interface device IDs, create/destroy routes and connections, eject and power interfaces, DME peer get/set, set power modes/hibernate, ping, and manage watchdog.

Control flow, state, and persistence: Host initialization creates SVC, negotiates version/hello, then SVC APIs issue Greybus SVC operations to configure topology and interface power. Device IDs, watchdog state, debugfs rail state, and protocol version persist in `gb_svc`.

Dependencies/integration: It integrates host devices, Greybus operations, SVC protocol payloads, IDA, workqueues, debugfs, and interface lifecycle.

Risks and test signals: Route/connection creation must be paired with destruction; DME/power-mode operations are topology- and quirk-sensitive. Tests should cover protocol negotiation, connection create/destroy failure unwind, route cleanup, interface power toggles, DME endian values, pwrmon bounds, ping timeout, watchdog enable/disable and bite action.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/greybus/svc.h -->
