# sources/distributed-fs/ceph-client/drivers/net/ethernet/mscc/ocelot_police.h

## Purpose
Defines the Ocelot policing configuration interface: rate modes, policer configuration fields, and helper prototypes for programming and validating policers.

## Important APIs/types/functions
`enum mscc_qos_rate_mode` covers disabled, line, data, and frame rate modes. `struct qos_policer_conf` contains DLB, coupling, CIR/CBS, PIR/PBS, and IPG fields. Prototypes are `qos_policer_conf_set` and `ocelot_policer_validate`.

## Control flow, state, persistence
No executable flow. The structure models hardware policers, where mode chooses units, DLB adds CIR, coupling can add CIR into PIR, and zero rate/burst is interpreted by implementation as discard.

## Dependencies and integration
Includes `ocelot.h` and flow offload APIs. Used by `ocelot_police.c`, `ocelot_net.c`, and `ocelot_flower.c`.

## Risks and test signals
Risk is caller confusion about kbps/fps and byte/frame burst units. Test by compiling all consumers and exercising every mode through `qos_policer_conf_set`.
