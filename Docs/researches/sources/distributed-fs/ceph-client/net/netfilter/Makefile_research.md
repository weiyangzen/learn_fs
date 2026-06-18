# sources/distributed-fs/ceph-client/net/netfilter/Makefile

## Purpose

This Makefile maps netfilter Kconfig symbols to kernel objects and composite modules. It is the build assembly point for core netfilter, nfnetlink modules, conntrack, NAT, nf_tables, flow tables, xtables matches and targets, ipset, IPVS, and lwtunnel hooks.

## Important Build Rules

`netfilter-objs := core.o nf_log.o nf_queue.o nf_sockopt.o utils.o` defines the built core module assembled when `CONFIG_NETFILTER` is enabled. `nf_conntrack-y` and `nf_nat-y` define composite objects for connection tracking and NAT, with optional members added by Kconfig symbols such as timeout, timestamp, events, labels, OVS, SCTP, GRE, redirect, masquerade, and BTF support. BTF object inclusion differs for module versus built-in builds using `CONFIG_DEBUG_INFO_BTF_MODULES` and `CONFIG_DEBUG_INFO_BTF`.

The file registers one object per nfnetlink subsystem, helper, nftables expression, flow table component, x_tables target, and x_tables match. `nf_tables-objs` includes the nftables core and built-in expression/set implementations, conditionally adding `nft_set_pipapo_avx2.o` on x86_64 non-UML and `nft_ct_fast.o` when `CONFIG_NFT_CT` and retpoline mitigation are configured. The ipset and IPVS directories are included with `obj-$(CONFIG_IP_SET) += ipset/` and `obj-$(CONFIG_IP_VS) += ipvs/`.

## Control Flow And State

The control flow is Kbuild symbol expansion. `obj-$(CONFIG_...)` emits objects for built-in `y` or module `m`, while composite `foo-y` variables define module internals. Conditional `ifeq`, `ifdef`, and `ifndef` blocks adjust object composition for debug BTF, architecture acceleration, retpoline support, and UML exclusions.

There is no runtime state. The persistent effect is the generated build graph, module names, and built-in object composition derived from `.config`.

## Dependencies And Integration

This file must stay aligned with `net/netfilter/Kconfig` and the actual source files in the same directory. It also integrates with subdirectory Makefiles for ipset and IPVS and with architecture/runtime features such as x86 AVX2 and retpoline. Externally, its module names are loaded by userspace tools and kernel module autoload paths, so object renames or symbol mismatches can break runtime firewall tools.

## Risks

Missing an object in a composite module can produce link-time undefined symbols or runtime missing functionality. Adding an object under the wrong symbol can build code without required dependencies. The BTF conditional handling is subtle because module and built-in builds use different debug symbols. Architecture-specific nftables acceleration must avoid unsupported builds, which is why the AVX2 object is guarded by both x86_64 and not UML.

## Test Signals

Useful tests include `make M=net/netfilter`, `make allmodconfig`, `make allyesconfig`, `make randconfig`, and explicit module load tests for `nf_conntrack`, `nf_nat`, `nf_tables`, xtables matches, `ip_set`, and `nf_hooks_lwtunnel`. Build logs should show no orphaned Kconfig symbols or missing object files.
