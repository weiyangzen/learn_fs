# sources/distributed-fs/ceph-client/net/netfilter/nf_nat_tftp.c

## Purpose

`nf_nat_tftp.c` is the NAT helper for TFTP conntrack expectations. TFTP control traffic negotiates a new UDP data flow, and this helper adjusts the related expectation so the data connection follows the NAT mapping of the master control connection.

## Important APIs, types, and functions

- `nat_helper_tftp` is a `struct nf_conntrack_nat_helper` initialized with `NF_CT_NAT_HELPER_INIT("tftp")`.
- `help()` is the callback installed into the global `nf_nat_tftp_hook` RCU pointer. It receives the packet, conntrack direction metadata, and a prepared expectation from the TFTP conntrack helper.
- `nf_ct_expect_related()` commits the adjusted expectation.
- `nf_nat_follow_master` is assigned as `exp->expectfn`, causing the related TFTP data connection to inherit NAT handling from the master flow.
- `nf_nat_tftp_init()` and `nf_nat_tftp_fini()` register and unregister the helper and hook.

## Control flow

On module initialization, the code asserts that no TFTP NAT hook is currently installed, registers the NAT helper, and publishes `help()` through `RCU_INIT_POINTER(nf_nat_tftp_hook, help)`. When the conntrack TFTP helper detects a related data flow, it calls this NAT hook with the expectation. `help()` reads the master conntrack from `exp->master`, saves the original client UDP source port in `exp->saved_proto.udp.port`, sets the expected direction to reply, assigns `nf_nat_follow_master`, and attempts to insert the expectation. Expectation insertion failure logs `"cannot add expectation"` and returns `NF_DROP`; success returns `NF_ACCEPT`.

## State and persistence behavior

There is no persistent storage. The only lasting runtime state is the registered NAT helper, the RCU hook pointer, and fields written into individual `struct nf_conntrack_expect` objects. Module exit unregisters the helper, clears `nf_nat_tftp_hook`, and waits for active RCU readers with `synchronize_rcu()` before unloading.

## Dependencies and integration points

This file depends on UDP headers, conntrack helper and expectation APIs, NAT helper registration, and the public TFTP conntrack hook declaration from `linux/netfilter/nf_conntrack_tftp.h`. It integrates with the TFTP conntrack parser, which owns protocol parsing and expectation allocation, while this file only supplies NAT-specific expectation mapping.

## Risks

The logic is intentionally small, so the main risk is ordering and lifetime: the RCU hook must be cleared only after helper unregistration, and module unload must wait for readers. Failed expectation insertion drops the triggering control packet, which is correct for consistency but can interrupt transfers when expectation table capacity is exhausted. Correctness also depends on the conntrack TFTP helper passing a valid expectation with `master` set.

## Test signals

Exercise a NATed TFTP read and write transfer and verify that the UDP data flow is expected in the reply direction and follows the master NAT mapping. Negative tests should cover expectation insertion failure, helper unload while traffic is active, and absence of stale hook use after unregister.
