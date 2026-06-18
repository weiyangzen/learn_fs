# sources/distributed-fs/lustre-release/lnet/klnds/efalnd/efalnd_modparams.c

## Purpose
This file defines EFALND module parameters and applies default/tunable values to LNet NI configuration during startup.

## Important APIs, Types, And Functions
Module parameters are `nscheds`, `nqps`, `credits`, `peer_credits`, `peer_buffer_credits`, `peer_timeout`, `rnr_retry_count`, and `ipif_name`. `kefalnd_tunables` exposes pointers to scheduler count, RNR retry count, and IP interface name. `kefalnd_tunables_init()` initializes default EFALND LND tunables. `kefalnd_tunables_setup()` copies defaults when no NI-specific tunables were supplied, stamps the LND version, fills common network tunables, clamps peer credits, enforces minimum connection timeout, and sets default QP count.

## Control Flow
Module parameter values are parsed by the kernel module subsystem before EFALND startup. At NI startup, `kefalnd_tunables_setup()` merges module defaults and NI/network tunables: unset common tunables (`-1`) are replaced, peer credits are clamped to EFALND min/max and max-tx credits, peer timeout is raised to `EFALND_MIN_INIT_CONN_TIMEOUT`, and zero `lnd_nqps` is replaced with the module `nqps`.

## State, Persistence, And Dependencies
Parameter values live in module memory and some are read-only after load (`0444`), while `rnr_retry_count` is writable (`0644`). `default_tunables` persists for future NI setup calls. The file depends on LNet default credit/timeout constants and EFALND version helpers.

## Integration Points
`efalnd.c` calls `kefalnd_tunables_init()` at module init and `kefalnd_tunables_setup()` during NI startup. QP count drives CQ/QP allocation; RNR retry drives QP RTS setup; `ipif_name` drives IPv4 underlay interface selection.

## Risks
Bad defaults can over-allocate QPs/TX pools or under-provision credits. Enforcing a minimum peer timeout may surprise configurations that attempt shorter failure detection. Writable `rnr_retry_count` affects new QPs but not necessarily existing QPs. `ipif_name` must select an IPv4 interface or startup fails.

## Test Signals
Tests should load with default parameters, explicit QP/scheduler/credit settings, invalid low peer credits/timeouts, runtime RNR changes before creating a new NI, missing or IPv6 `ipif_name`, and NI-specific tunables overriding module defaults.
