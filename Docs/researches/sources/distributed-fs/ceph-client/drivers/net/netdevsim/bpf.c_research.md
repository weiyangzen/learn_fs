# sources/distributed-fs/ceph-client/drivers/net/netdevsim/bpf.c

## Purpose
This file implements netdevsim's BPF and XDP offload simulation. It provides fake verifier/offload callbacks, debugfs-controlled accept/reject knobs, TC classifier offload handling, XDP driver and hardware attach paths, and a tiny in-memory implementation of offloaded BPF array/hash maps for selftests.

## Important APIs, Types, and Functions
`struct nsim_bpf_bound_prog` tracks an offloaded program's owning simulated device, BPF program pointer, debugfs directory, verifier state string, loaded flag, and list membership. `struct nsim_bpf_bound_map` tracks an offloaded map, a mutex, and up to two key/value entries. Important entry points are `nsim_bpf_setup_tc_block_cb()`, `nsim_bpf_disable_tc()`, `nsim_bpf()`, `nsim_bpf_dev_init()`, `nsim_bpf_dev_exit()`, `nsim_bpf_init()`, and `nsim_bpf_uninit()`. Offload callbacks are exposed through `struct bpf_prog_offload_ops nsim_bpf_dev_ops` and `struct bpf_map_dev_ops nsim_bpf_map_ops`.

## Control Flow
When an offloaded program is prepared, `nsim_bpf_verifier_prep()` checks `bpf_bind_accept`, creates program state, debugfs files, and stores state in `prog->aux->offload->dev_priv`. The verifier instruction hook can delay on the first instruction, logs a message on the last instruction, and rejects if `bpf_bind_verifier_accept` is false. Translation marks state as `xlated`; destroy warns if still loaded, removes debugfs, unlinks, and frees state. TC offload validates type, chain, protocol, debugfs accept flags, and bound-program requirements, then swaps `ns->bpf_offloaded`. XDP driver attach validates non-offloaded programs and MTU constraints; XDP hardware attach requires a translated offloaded program and shares the same single hardware offload slot with TC. Map allocation accepts only array/hash maps with at most two entries and no map flags, installs map ops, and stores data in kernel memory.

## State and Persistence
All state is runtime and debugfs-visible. Per-device debugfs toggles control verifier acceptance, verifier delay, TC acceptance, unbound TC acceptance, XDP driver/hardware acceptance, and map acceptance. Program and map lists live under `nsim_dev`; netdev-specific state stores current XDP attachments and the currently offloaded BPF id. Offloaded maps persist until BPF frees them; their key/value entries are protected by a mutex.

## Dependencies and Integration Points
The file integrates with BPF verifier/offload infrastructure, TC classifier offload, XDP attachment helpers, rtnetlink locking, debugfs, netdevsim device lifecycle, and packet classifier extack reporting. It depends on `netdevsim.h` for simulator structures and debugfs directories.

## Risks and Edge Cases
Only one TC or hardware XDP program can occupy the simulated offload slot, so the code rejects conflicting loads. The TC path treats old-program mismatches carefully to avoid removing a program that no longer matches driver state. Offloaded array map allocation initializes all two possible slots, regardless of requested `max_entries` bounded to two; callers rely on BPF map metadata for valid indexes. Map list operations are not protected by an explicit list lock here, relying on offload lifecycle serialization. MTU checks reject XDP programs without frag support when MTU exceeds `NSIM_XDP_MAX_MTU`.

## Test Signals
Selftests can flip debugfs booleans to force verifier, TC, XDP, and map failures; observe bound program debugfs directories with `state`, `id`, and `loaded`; load and unload TC and XDP offloads; attempt conflicting TC/XDP hardware programs; exercise offloaded hash and array map lookup/update/delete/next-key operations; and verify cleanup warnings do not fire after normal unload.
