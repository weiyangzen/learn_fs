# sources/distributed-fs/openafs/src/venus/twiddle.c

## Purpose
`twiddle.c` implements a hidden/diagnostic-style `fs`-named utility for adjusting RX transport parameters in the cache manager through `VIOC_TWIDDLE`. It packages command-line numeric values into `struct rxparams` and sends them to the local client.

## Important APIs, Types, And Functions
`Twiddle` parses optional numeric command parameters into `rx_initReceiveWindow`, `rx_maxReceiveWindow`, `rx_initSendWindow`, `rx_maxSendWindow`, `rxi_nSendFrags`, `rxi_nRecvFrags`, `rxi_OrphanFragSize`, `rx_maxReceiveSize`, and `rx_MyMaxSendSize`. `main` registers one command syntax with those nine parameters. `Die` formats common pioctl/errno failures.

## Control Flow
Startup applies the AIX full-core signal action when relevant, registers the single syntax, dispatches, conditionally finalizes RX, and exits. The command handler treats omitted parameters as zero, uses `atoi` without range checking, sends the filled structure as both input and output through `pioctl(0, VIOC_TWIDDLE, &blob, 1)`, and reports errors through `Die`.

## State And Persistence
Local state is temporary, but the pioctl can change cache-manager RX runtime behavior such as window sizes, fragment counts, and max send/receive sizes. Those changes are runtime cache-manager state, not local file edits.

## Dependencies And Integration Points
The file depends on OpenAFS Venus pioctl definitions, RX parameter structures, command parsing, and cache-manager support for `VIOC_TWIDDLE`. It is coupled to the cache manager's interpretation of zero values and the exact `struct rxparams` layout.

## Risks And Test Signals
Risks include no numeric validation, parameter names containing trailing spaces in `cmd_AddParm`, confusing program name `pn` set to `fs`, error reporting that ignores the handler's `code` argument and uses global `errno`, and easy destabilization of RX behavior with bad values. Test signals include pioctl success with safe values, expected rejection for invalid/unsupported clients, and observable RX behavior or diagnostics changing after parameter updates.
