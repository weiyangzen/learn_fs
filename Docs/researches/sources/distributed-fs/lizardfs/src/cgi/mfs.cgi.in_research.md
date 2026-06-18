# sources/distributed-fs/lizardfs/src/cgi/mfs.cgi.in

## Purpose
`mfs.cgi.in` is the Python 3 CGI dashboard template for the LizardFS web UI. CMake substitutes protocol constants such as `@PROTO_BASE@` and chart identifiers, then the script connects directly to the master and chunkservers over LizardFS binary protocols to render XHTML status tables, controls, and chart image links.

## Important APIs, Types, And Functions
- Protocol command constants cover older MooseFS-style messages, LizardFS-specific master requests, chunkserver HDD list requests, metadata-server discovery, chunk health, custom goals, and server removal.
- The mini serialization/deserialization DSL is built from `Primitive`, `Tuple`, `String`, `List`, `Dict`, and `deserialize`. It consumes a mutable `bytearray` in network byte order and supports nested lists/dicts for newer LizardFS packets.
- `make_liz_message` builds modern LizardFS packets with type, payload length including version, and version.
- `send_and_receive`, `mysend`, and `myrecv` provide blocking socket I/O, exact byte reads/writes, response type checks, and optional response version checks.
- `cltoma_list_goals`, `cltoma_chunks_health`, `cltoma_metadataservers_list`, `cltoma_hostname`, and `cltoma_metadataserver_status` are higher-level protocol helpers.
- `createlink` and `createorderlink` preserve CGI query parameters and construct sort/toggle URLs for every table.
- `LessThanComparableNone` mimics Python 2 sortable `None` behavior so rows with absent limits can be sorted with concrete values.

## Control Flow
On startup the script reads CGI fields for `masterhost`, `masterport`, and `mastername`, falling back to DNS name `mfsmaster`, port `9421`, and display name `LizardFS`. It probes the master using `CLTOMA_INFO`; response length determines historical master versions, while newer responses embed version bytes. Failure renders a standalone connection-error page with an address form and exits.

After version detection, command handling runs before normal rendering. The only mutating command in this file is `CSremove`, which parses `ip:port`, sends `CLTOMA_CSSERV_REMOVESERV`, and either redirects back to the same page without the command parameter or shows an error page with optional traceback.

The page then chooses visible sections from the `sections` query parameter. Available sections vary by master version: older masters expose `IN`, `CS`, `HD`, `ML`, charts, and help; newer masters add chunks, exports/config, mount parameters, and mount operations. Each active section appends a self-contained table, usually inside a `try` block that renders Python tracebacks into an exception table instead of aborting the page.

The `IN` section renders master info for multiple protocol-era record sizes, chunk matrix status, chunk operation loop status, and filesystem check status. The `CH` section uses `LIZ_CLTOMA_CHUNKS_HEALTH` plus goal definitions to render availability, replication, and deletion summaries. The `CS` section renders metadata servers when supported, chunkserver capacity/status, and metadata backup loggers. The `HD` section first discovers live chunkservers from the master, then queries each chunkserver's HDD list protocol, selecting V1 or V2 by chunkserver version and deriving throughput/time/space columns. `EX`, `ML`, `MS`, and `MO` decode exports and client sessions in several historical layouts. `MC` and `CC` mostly generate JavaScript and `chart.cgi` image URLs for master and chunkserver charts.

## State And Persistence
The script itself persists no server-side state. All state is per-request CGI input, transient sockets, and local variables. It reads live state from master/chunkserver processes and links chart images served by `chart.cgi`, whose backing data is maintained elsewhere. The mutating `CSremove` path changes master-managed chunkserver state by asking the master to remove a disconnected server.

## Dependencies And Integration Points
It depends only on Python standard library modules, the CGI runtime, generated CMake substitutions, `mfs.css`, static images, and `chart.cgi`. Its protocol contracts must stay aligned with LizardFS master/chunkserver packet layouts in C++ protocol code. It integrates with web servers as a CGI script and assumes direct TCP access to the master and chunkservers.

## Risks
- The file performs raw binary decoding with many version/length branches; a protocol layout drift can silently misrender rows or consume offsets incorrectly.
- Most socket calls are blocking and have no explicit timeout, so slow or unreachable chunkservers can stall a CGI request.
- Query fields are generally escaped for output with `htmlentities` or URL-escaped for links, but some decoded protocol strings and traceback paths are inserted directly in places; XSS risk depends on whether those values can be attacker controlled.
- `print_file` opens arbitrary names but is unused in production help output. It would be risky if reconnected to query-driven input.
- The script uses deprecated `cgi`/`cgitb` APIs in modern Python, so future interpreter upgrades may require replacement.
- One sorting branch in exports sets `EXorder == 14` to `mapalluid` instead of `mapallgid`, which looks like a display/sort bug.

## Test Signals
No direct unit tests are present for this CGI script in the listed files. Practical validation should include master-version compatibility tests, packet fixture decoding for each historical branch, CGI rendering smoke tests with escaped strings, and integration tests against a test master/chunkserver pair.
