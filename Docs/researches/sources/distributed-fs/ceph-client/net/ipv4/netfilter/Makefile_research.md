# sources/distributed-fs/ceph-client/net/ipv4/netfilter/Makefile

## Purpose
The Makefile maps IPv4/ARP netfilter Kconfig symbols to object files and composite objects.

## Important APIs, Types, And Functions
It builds defrag, socket/tproxy, reject, NAT helpers, nftables IPv4 expressions, legacy iptables core and table instances, legacy matches/targets, legacy arptables core/table/target modules, and `nf_dup_ipv4.o`. `nf_nat_snmp_basic-y` demonstrates a composite module with generated ASN.1 support.

## Control Flow
Object selection follows `obj-$(CONFIG_...) += ...`; composite module prerequisites are declared before the corresponding `obj-*` line. Build order groups defrag/core helpers, NAT helpers, nft modules, legacy IP tables, matches, targets, ARP tables, and duplicate support.

## State And Persistence
No runtime state; it persists build composition in kbuild metadata.

## Dependencies And Integration Points
The file must stay aligned with Kconfig symbols and source filenames in this directory. It also integrates generated ASN.1 header dependencies for SNMP NAT.

## Risks
Risks are stale symbol/object mappings, missing composite dependencies, modules built without their Kconfig gate, and mismatches between backward-compatible Kconfig selector names and actual object names.

## Test Signals
Use `make net/ipv4/netfilter/` or kernel config matrix builds to verify each symbol selects the expected object, especially `IP_NF_IPTABLES_LEGACY`, table modules, ARP modules, `NF_NAT_H323`, `NF_DEFRAG_IPV4`, and nftables IPv4 modules.
