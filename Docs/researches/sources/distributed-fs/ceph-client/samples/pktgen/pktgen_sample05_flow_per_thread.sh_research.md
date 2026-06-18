# sources/distributed-fs/ceph-client/samples/pktgen/pktgen_sample05_flow_per_thread.sh

## Purpose

This sample creates one deterministic UDP/IP flow per pktgen thread. It is designed to test receiver-side scalability by giving each transmit CPU a distinct fixed source IP while sharing one destination.

## Important APIs, Types, and Functions

It uses common pktgen helper functions and variables from `parameters.sh`. Important pktgen controls include `QUEUE_MAP_CPU`, fixed `src_min/src_max`, `burst`, common packet attributes, optional destination-port randomization, and optional UDP checksum.

## Control Flow

The script defaults destination IP/MAC, `CLONE_SKB=0`, `BURST=32`, and infinite count. For each configured thread, it creates `$DEV@$thread`, maps queue-to-CPU, sets common packet fields, assigns a fixed source address `198.18.$((thread+1)).1`, and enables burst unless `BURST=0`. It starts all configured threads through pgctrl unless appending.

## State and Persistence Behavior

The meaningful state is per-thread pktgen configuration. Each thread has a stable source address based on thread id, making receiver flow placement repeatable across runs as long as thread selection is unchanged.

## Dependencies and Integration Points

It integrates with receiver RSS/flow steering and sender multiqueue behavior. It needs pktgen procfs, helper scripts, root privileges, and a valid destination MAC.

## Risks and Edge Cases

The source IP formula assumes thread ids fit into the third octet range. If thread ids are high, generated IPs can be invalid. Infinite count and burst mode can saturate network equipment.

## Test Signals

Capture traffic to confirm one source IP per thread, check per-thread pktgen results, and inspect receiver queue/CPU distribution.
