# sources/distributed-fs/ceph-client/net/openvswitch/meter.c

## Purpose
`meter.c` implements Open vSwitch datapath meter management and packet metering execution. It exposes the OVS meter generic-netlink family, stores per-datapath meters in an RCU array, and implements a token-bucket-like drop band decision used by action execution.

## Important APIs, Types, and Functions
Netlink attribute policies `meter_policy` and `band_policy` validate `OVS_METER_ATTR_*` and `OVS_BAND_ATTR_*` command attributes. `dp_meter_instance_alloc()`, `dp_meter_instance_realloc()`, insert/remove helpers, `attach_meter()`, and `detach_meter()` manage a dynamically resized array indexed by `meter_id % n_meters`.

Command handlers are `ovs_meter_cmd_features()`, `ovs_meter_cmd_set()`, `ovs_meter_cmd_get()`, and `ovs_meter_cmd_del()`, exported through `dp_meter_genl_family`. `dp_meter_create()` validates a meter definition, requires at least one band and no more than `DP_MAX_BANDS`, supports only nonzero rates, initializes bucket size from burst size, computes `max_delta_t`, and optionally preserves supplied stats when clear is not requested. `ovs_meter_cmd_reply_stats()` serializes meter and band counters.

`ovs_meter_execute()` is the fast-path action helper. It looks up a meter, locks it, computes elapsed milliseconds since last use, caps delta to avoid bucket wrap, updates global meter stats, refills each band bucket by `delta_ms * rate`, charges either packet bits for kbps meters or `1000` units for packet-rate meters, chooses the exceeded band with the highest rate, updates band stats, and returns true when a drop band is triggered. Missing meters are ignored rather than dropping.

`ovs_meters_init()` allocates the initial meter table and caps allowed meters to the smaller of `DP_METER_NUM_MAX` or about 3.12 percent of available memory. `ovs_meters_exit()` frees all meters and the instance.

## Control Flow
Datapath creation initializes `dp->meter_tbl`. Userspace configures meters through generic netlink; set replaces any old meter under OVS mutex, replies with old stats when present, then RCU-frees the old object. Action validation in `flow_netlink.c` accepts meter ids without requiring existence. During action execution, `actions.c` calls `ovs_meter_execute()` and drops with `OVS_DROP_METER` when it returns true.

## State and Persistence
Meter state is volatile per datapath. `struct dp_meter` stores id, flags, bands, stats, `used` time, and per-meter spinlock. The containing `dp_meter_instance` is RCU-replaceable for resize and shrink. Meter stats and token buckets persist until meter replacement, deletion, datapath teardown, or explicit clear semantics on set.

## Dependencies and Integration Points
It depends on OVS datapath locking and lookup, generic netlink, RCU, `meter.h`, and `datapath.h`. It integrates with action execution via `ovs_meter_execute()` and with `datapath.c` module registration through `dp_meter_genl_family`.

## Risks
The array uses direct modulo hashing and expects userspace/id-pool allocation to avoid occupied slots; collisions return `-EBUSY`. Resize and shrink must preserve slot positions to keep modulo lookup valid. Token bucket arithmetic depends on units being consistent for kbps and packet-rate modes. Concurrent execution is serialized per meter, but command replacement relies on RCU grace before freeing old meters. `DP_MAX_BANDS` is one, so userspace expecting multi-band meters will be rejected.

## Test Signals
Useful tests include meter feature/get/set/delete generic-netlink commands, replacement preserving or clearing stats, nonexistent meter actions being no-ops, drop behavior around rate/burst boundaries, kbps versus packet-rate accounting, concurrent packet execution against meter replacement, and datapath teardown leak checks.
