# Research: sources/cloud-native/moby/daemon/libnetwork/etchosts/etchosts.go

Purpose: builds and mutates container `/etc/hosts` files. Important types/APIs are `Record`, `Record.WriteTo`, `Build`, `BuildNoIPv6`, `Add`, `Delete`, `Update`, `Drop`, and the internal path-level lock cache.

Control flow: `Build` writes default IPv4/IPv6 localhost records plus extras; `BuildNoIPv6` filters IPv6 extra records and writes IPv4-only defaults. `Add` appends formatted records. `Delete` scans the file, preserves comments and nonmatching lines, and removes only records whose parsed address and exact tab-suffixed host string match. `Update` uses a hostname-bound regular expression to replace IPs for matching hostnames without matching prefixed names. All mutating operations acquire a lock unique to the file path.

State/dependencies: state is only the lock map; persistence is the hosts file itself. Dependencies include `netip`, `bufio`, regex, and OS file IO. Risks include lock map growth unless `Drop` is called, exact tab-format dependency in deletion, and regex behavior around unusual hostnames. Tests cover default ordering, no-IPv6 filtering, update/delete prefix regressions, empty inputs, newline handling, concurrency, and fuzzing `Add`.
