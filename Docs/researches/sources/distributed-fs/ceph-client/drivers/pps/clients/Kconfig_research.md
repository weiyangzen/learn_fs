# sources/distributed-fs/ceph-client/drivers/pps/clients/Kconfig

Purpose: configuration menu for PPS input clients.

Important entries: `PPS_CLIENT_KTIMER` is a debug timer source; `PPS_CLIENT_LDISC` depends on `TTY` and captures serial carrier-detect changes; `PPS_CLIENT_PARPORT` depends on `PARPORT`; `PPS_CLIENT_GPIO` captures PPS from a GPIO-backed platform device.

Control flow/state: configuration-only. Each option maps to a client object in the clients Makefile and depends on the PPS core APIs at runtime.

Dependencies/integration: TTY line discipline, parallel-port subsystem, GPIO descriptor/platform firmware, and timer APIs.

Risks/test signals: verify menu dependencies hide unavailable clients, module names match help text, and selected clients link against exported `pps_register_source()`, `pps_unregister_source()`, and `pps_event()`.
