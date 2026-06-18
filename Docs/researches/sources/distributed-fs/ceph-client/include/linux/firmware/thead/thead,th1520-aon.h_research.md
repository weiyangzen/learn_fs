# sources/distributed-fs/ceph-client/include/linux/firmware/thead/thead,th1520-aon.h

## Purpose
This header describes the T-Head TH1520 always-on firmware RPC ABI used for power, watchdog, low-power, miscellaneous, and system services.

## APIs, types, and control flow
It defines service ids (`TH1520_AON_RPC_SVC_*`), per-service function ids for misc, watchdog, system, low-power, and power management, and packed wire structures `th1520_aon_rpc_msg_hdr` plus `th1520_aon_rpc_ack_common`. Header access macros set/get version, service id, message type, and ack type by bit packing into `svc`. Runtime entry points are `th1520_aon_init(dev)`, `th1520_aon_deinit()`, `th1520_aon_call_rpc(aon_chan, msg)`, and `th1520_aon_power_update(aon_chan, rsrc, power_on)`.

## State and dependencies
The opaque `struct th1520_aon_chan` owns channel state. Message headers are packed/aligned for firmware transport, and constants encode power modes and power-domain ids such as audio, video, NPU, GPU, and DSP islands.

## Integration, risks, and tests
Power domain, watchdog, suspend, and low-power drivers use this as their firmware transport. Risks include bit-setting macros using OR semantics on uncleared fields, packed ABI drift, wrong message sizes, missing ack handling, and concurrent RPC serialization. Tests should check init/deinit lifetime, header encode/decode, ack error-code paths, power-domain toggles, watchdog commands, and suspend/resume RPC ordering.
