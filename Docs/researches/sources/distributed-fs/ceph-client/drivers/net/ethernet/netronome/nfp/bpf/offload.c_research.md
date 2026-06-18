<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/bpf/offload.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/bpf/offload.c

## Purpose
This file connects the Linux BPF offload core to NFP firmware. It prepares and destroys per-program compiler state, translates verified BPF to NFP instructions, manages offloaded maps and neutral map references, implements map device ops with firmware control messages, handles async perf-event output, checks MTU/program/stack limits, and loads/unloads BPF programs into vNIC firmware state.

## Important APIs, Types, And Functions
- Program offload ops: `nfp_bpf_verifier_prep()`, `nfp_bpf_translate()`, and `nfp_bpf_destroy()` are exported through `nfp_bpf_dev_ops`.
- Program metadata: `nfp_prog_prepare()` builds the instruction metadata list; `nfp_prog_free()` tears it down.
- Neutral map tracking: `nfp_map_ptrs_record()`, `nfp_map_ptr_record()`, and `nfp_map_ptrs_forget()` hold references to offload-neutral maps used by programs.
- Map device ops: `nfp_bpf_map_alloc()`, `nfp_bpf_map_free()`, `nfp_bpf_map_lookup_entry()`, `nfp_bpf_map_update_entry()`, `nfp_bpf_map_get_next_key()`, and `nfp_bpf_map_delete_elem()`.
- Firmware program load: `nfp_bpf_offload_check_mtu()`, `nfp_net_bpf_load()`, `nfp_net_bpf_start()`, `nfp_net_bpf_stop()`, and `nfp_net_bpf_offload()`.
- Event output: `nfp_bpf_event_output()` maps firmware events back to host perf-event maps.

## Control Flow
When BPF offload begins, prepare allocates `struct nfp_prog`, attaches it to `prog->aux->offload->dev_priv`, copies eBPF instructions into metadata, and records jump/subprogram metadata. Translate rejects failed verifier optimizations, allocates a maximum-size image based on vNIC config, calls `nfp_bpf_jit()`, exposes the JIT image to BPF core, and records neutral maps. Destroy frees the image, releases neutral-map references after RCU synchronization if needed, and frees metadata.

Map allocation validates firmware map capabilities, flags, NUMA node, map type, resource limits, key/value sizes, and element size. It allocates NFP private map state, asks firmware for a table id, installs device ops, increments app resource counters, and links the map. Free reverses the firmware and host state, warns on outstanding cache blockers, and releases cached skbs.

Program load checks packet boundary, stack size, and program length, obtains a per-vNIC relocated/ECC image from the JIT, DMA maps it, writes firmware BPF size/address registers, and triggers `NFP_NET_CFG_UPDATE_BPF`. Starting/stopping toggles `NFP_NET_CFG_CTRL_BPF` through a generic reconfig. Live reload requires firmware relocation capability.

## State And Persistence
Runtime state includes per-program generated image and map records, per-map firmware table id/cache/use map, app map counters/list, neutral-map rhashtable records with refcounts, and vNIC BPF control bit. Firmware persists loaded program image and map table contents until unload, map free, or device reset. No disk persistence exists.

## Dependencies And Integration Points
The file depends on Linux BPF offload core, BPF map APIs, netdev/PCI/DMA APIs, TC action headers, NFP netdev control registers/reconfig, CCM map operations from `cmsg.c`, JIT/verifier hooks from `main.h`, and firmware ABIs from `fw.h`.

## Risks And Edge Cases
- `nfp_bpf_translate()` returns without freeing `nfp_prog->prog` on JIT error; later destroy must run or memory can remain attached to failed offload state.
- Map value endian conversion is necessary for atomic counters; mixed read/atomic or non-zero initialization paths are rejected or marked by verifier/offload code.
- Neutral-map references require RCU synchronization before `bpf_map_put()` and free, because event output looks them up under RCU.
- Live reload is refused unless firmware advertises relocation capability; otherwise active BPF control state would be overwritten unsafely.
- Firmware free-map failures can leak device-side maps even though host state is being destroyed.
- Async event output cannot report lost/rejected events synchronously to the BPF program.

## Test Signals
Validate BPF offload prepare/translate/destroy, map allocation limit failures, map endian behavior with atomics, neutral perf-event map references, event delivery to perf rings, DMA load/unload and reconfig errors, live reload with/without firmware relocation capability, MTU/stack/program length rejection, map delete rejection for arrays, and cleanup warnings for cache blockers or leaked map counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/bpf/offload.c -->
