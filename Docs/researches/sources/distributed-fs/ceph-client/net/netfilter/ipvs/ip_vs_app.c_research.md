# sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_app.c

## Purpose

`ip_vs_app.c` provides IPVS application-helper infrastructure. It lets protocol helpers such as FTP register application instances, bind helpers to IPVS connections, rewrite payload-related TCP sequence/ack numbers after packet mangling, expose helper state through procfs, and clean helper registrations per network namespace.

## Important APIs, types, and functions

Exported registration APIs are `register_ip_vs_app()`, `unregister_ip_vs_app()`, and `register_ip_vs_app_inc()`. `ip_vs_app_inc_new()` clones an app into a protocol/port incarnation, creates timeout tables if provided, and calls the protocol's `register_app` hook. `ip_vs_app_inc_release()` unregisters the incarnation and frees it through RCU. `ip_vs_app_inc_get()` and `ip_vs_app_inc_put()` pair module references with incarnation use counts. `ip_vs_bind_app()` delegates to protocol app binding, while `ip_vs_unbind_app()` calls helper unbind/done hooks and drops the incarnation reference. Packet hooks `ip_vs_app_pkt_in()` and `ip_vs_app_pkt_out()` call helper `pkt_in`/`pkt_out` callbacks and use `vs_fix_seq()`, `vs_fix_ack_seq()`, and `vs_seq_update()` for TCP sequence delta tracking.

## Control flow

Registration is serialized by `__ip_vs_app_mutex`. A base app is copied into `ipvs->app_list`, and incarnations are copied from that base and inserted into both protocol app state and the app's incarnation list. Packet processing checks `cp->app`; non-TCP helpers call callbacks directly, while TCP paths first ensure the TCP header is writable, adjust sequence/ack numbers based on prior payload length changes, invoke the helper callback, then update connection sequence delta state if the helper changed packet length. Procfs iteration locks the same mutex and walks all apps and incarnations.

## State and persistence behavior

Per-netns app state lives in `ipvs->app_list`. Each incarnation stores protocol, port, timeout table, use count, callback pointers, and parent app pointer. Connection-specific state lives in `cp->app`, `cp->app_data`, `cp->in_seq`, `cp->out_seq`, and sequence flags. Incarnations are RCU-freed after unregister, and module use counts prevent unloading while incarnations are active.

## Dependencies and integration points

The file depends on IPVS protocol hooks, module reference counting, RCU, procfs seq_file support, TCP header manipulation, skb writeability, and net namespace lifecycle. It integrates with `ip_vs_conn.c` connection creation/destruction, protocol modules that register helper ports, and helper modules such as FTP.

## Risks

Sequence delta logic is sensitive: incorrect `diff` handling can corrupt TCP streams after payload mangling. Helper callbacks run on packet paths and must handle writable skb failures. Registration and proc iteration share a mutex, while active packet users rely on module refs and RCU; lifetime regressions can lead to use-after-free or unload races. Per-netns cleanup must unregister all helpers before proc removal.

## Test signals

Tests should register duplicate and distinct apps, register incarnations for supported/unsupported protocols, bind/unbind helpers to connections, mangle TCP payload lengths and validate sequence/ack correction in both directions, exercise non-TCP callbacks, read `/proc/net/ip_vs_app`, and clean up network namespaces with active helper registrations.
