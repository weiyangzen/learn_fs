# sources/cloud-native/containers-storage/pkg/system/meminfo_freebsd.go

Purpose: implements FreeBSD memory and swap statistics retrieval.

Important APIs, types, and functions: `getMemInfo`, `getSwapInfo`, and `ReadMemInfo`.

Control flow: `getMemInfo` reads `vm.vmtotal`, validates struct size, and combines page size with physical page/free counts. `getSwapInfo` reads swap device count, iterates `vm.swap_info`, validates sizes, and accumulates total and used blocks. `ReadMemInfo` combines memory and swap values and rejects negatives.

State and persistence: reads kernel sysctl state; no mutation.

Dependencies and integration points: depends on cgo FreeBSD headers, `errors`, `fmt`, `unsafe`, and `x/sys/unix`; selected on `freebsd && cgo`.

Risks and edge cases: cgo and exact C struct sizes are required. Swap block/page unit assumptions must match FreeBSD kernel ABI.

Test signals: no FreeBSD meminfo tests in requested files.
