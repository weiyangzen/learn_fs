
# sources/distributed-fs/openafs/src/ubik/uinit.c

`uinit.c` implements generic Ubik client initialization from AFS cell configuration and security settings. It hides config-directory lookup, cell host discovery, Rx security object creation, and `ubik_ClientInit` connection assembly behind several convenience APIs.

Important APIs are `ugen_ClientInitCell`, `ugen_ClientInitServer`, `ugen_ClientInitFlags`, and legacy `ugen_ClientInit`; internal helpers are `internal_client_init` and `internal_client_init_dir`. `internal_client_init_dir` opens a config directory, selects a cell name, retrieves `afsconf_cell` host information for a service id, and delegates. `internal_client_init` calls `rx_Init`, sets dead time, chooses a client security object via `afsconf_PickClientSecObj`, optionally reports fallback to null authentication, invokes a caller security callback, builds Rx connections either to one explicit server or every cell server, and initializes a `struct ubik_client`.

State is transient: a static `serverconns[MAXSERVERS]` array is reused during initialization and the resulting ownership is handed to Ubik client structures. Security flags combine local-auth, no-auth, fallback-null, and always-encrypt options. There is no file persistence beyond reading CellServDB/config data through afsconf.

Dependencies include Rx, `afsconf`, AFS auth/key configuration, dirpath constants, `ubik_ClientInit`, and service ids. Risks include the static connection array, maxserver checks, possible null-security fallback when tokens are unavailable, and confusing interaction between `serviceid` strings and numeric `usrvid` service ids. Test signals include explicit-server initialization, configured-cell initialization, noauth/localauth paths, too many configured servers, failed config open/cell lookup, and security callback invocation.
