# Chunk Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/services/authzone.c lines 1-8713

## Scope

This chunk covers almost all of `authzone.c`, the Unbound/OpenBSD unwind authoritative-zone implementation for locally hosted zones. It includes zone data storage, zonefile parsing/writing, answer generation, DNSSEC denial proof generation, RPZ integration hooks, NOTIFY handling, AXFR/IXFR/HTTP zone transfer state machines, ZONEMD hash/DNSSEC verification, and the start of memory accounting.

## Main APIs Covered

- Zone lifecycle/config: `auth_zones_create`, `auth_zones_delete`, `auth_zones_apply_cfg`, `auth_zones_cleanup`.
- Zone lookup/answering: `auth_zones_lookup`, `auth_zones_downstream_answer`, `auth_zones_can_fallback`.
- Zonefile and SOA helpers: `auth_zone_read_zonefile`, `auth_zone_write_file`, `auth_zone_get_soa_rrset`, `auth_zone_get_serial`.
- Transfer lifecycle: `auth_xfer_create`, `auth_xfer_delete`, `auth_xfer_pickup_initial`, `auth_zones_notify`, `auth_zones_startprobesequence`, `xfer_set_masters`.
- Event callbacks: transfer/probe DNS lookups, timers, TCP, HTTP, UDP probe, and ZONEMD DNSKEY/DS lookup callbacks.
- ZONEMD helpers: `compare_serial`, `auth_zone_generate_zonemd_hash`, `auth_zone_generate_zonemd_check`, `auth_zone_verify_zonemd`.

## Core State

`auth_zones` owns `ztree` for zones and `xtree` for transfer state, plus RPZ list state. `auth_zone` stores zone identity, config flags, optional `zonefile`, optional RPZ, expiration state, and an rbtree of `auth_data` owner nodes. `auth_data` owns sorted `auth_rrset` lists. `auth_xfer` mirrors zone identity and SOA lease state, then coordinates `task_nextprobe`, `task_probe`, and `task_transfer`.

## Control Flow

Configuration flows through `auth_zones_apply_cfg`: mark old zones deleted, merge each `config_auth`, delete removed zones, read zonefiles, then initialize transfer SOA state. Zonefile parsing supports `$INCLUDE` up to `MAX_INCLUDE_DEPTH`, default TTL 3600, chroot path adjustment, and RPZ mirror updates.

RR mutation normalizes wire RRs into `packed_rrset_data`. RRSIGs are stored with covered RRsets when possible; otherwise they remain in an RRSIG rrset until moved. Transfer packet RRs are decompressed before insertion/removal.

Answer generation builds a regional `dns_msg`, finds exact/closest-encloser state, handles delegations, DNAME, wildcard, CNAME chains, ANY, NXDOMAIN, and NODATA, and adds NSEC/NSEC3 denial proofs where available. Downstream answering encodes directly; upstream lookup returns fallback decisions to the iterator path.

NOTIFY handling validates source addresses against configured masters/allow-notify entries, compares serials with RFC1982-style wrap logic, then starts or queues probe/transfer work. Transfers use three task layers: lease timer, SOA probe, and actual IXFR/AXFR/HTTP fetch.

Transfer completion accumulates chunks, validates DNS transfer packets, applies IXFR/AXFR/HTTP content, refreshes SOA lease state, runs ZONEMD verification, finishes RPZ config, optionally writes a temp zonefile and renames it into place, then schedules the next refresh/retry.

ZONEMD supports SIMPLE with SHA384/SHA512. It canonicalizes zone RRsets, omits apex ZONEMD and RRSIGs over apex ZONEMD, verifies digest length/content, optionally verifies DNSSEC chain or DNSSEC absence proof, and expires the zone on failure unless permissive mode is enabled.

## Dependencies

Uses Unbound DNS message/rrset/cache structures, `sldns` wire and zonefile parsers, dname utilities, comm timers/points, outside network fetchers, mesh callbacks, validator trust-anchor/DNSSEC APIs, NSEC/NSEC3 helpers, RPZ APIs, and lock primitives.

## Risks And Edge Cases

- Lock ordering and callback re-entry are central risks; several paths unlock around `mesh_new_callback` and ZONEMD checks because callbacks may run immediately.
- IXFR apply mutates memory while parsing; soft failures can force AXFR refetch after partial changes.
- Packed rrset mutation uses manual size arithmetic and pointer fixups.
- `zonemd_simple_domain` allocates a large 65,536-entry rrset pointer array on the stack.
- HTTP zone parsing is custom line/chunk parsing and ignores includes.
- `parse_url` has limited validation around malformed ports.
- Expired-zone behavior differs between upstream/downstream and fallback settings.
- Chunk ends mid-helper at `auth_addrs_get_mem`; memory accounting continues after line 8713.

## Cross-Chunk References

The continuation after line 8713 completes memory accounting (`auth_addrs_get_mem`, `auth_primaries_get_mem`, `auth_chunks_get_mem`, `auth_xfer_get_mem`, `auth_zones_get_mem`) and includes `xfr_disown_tasks`. The final merged file report should connect these APIs to `services/authzone.h` and external iterator/worker callers.