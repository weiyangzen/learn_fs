# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfpcore/nfp.h

## Purpose

`nfpcore/nfp.h` is a compact public interface for NFP device access and query services. It declares hwinfo accessors, low-level NSP configuration/state helpers, NSP read/write commands, resource-table functions, and standard NFP resource names.

## Important APIs, Types, and Functions

Important declarations include `nfp_hwinfo_read()`, `nfp_hwinfo_lookup()`, packed hwinfo accessors, `nfp_nsp_cpp()`, NSP config modified/state helpers, `nfp_nsp_read_eth_table()`, `nfp_nsp_write_eth_table()`, `nfp_nsp_read_identify()`, `nfp_nsp_read_sensors()`, `nfp_resource_table_init()`, `nfp_resource_acquire()`, `nfp_resource_release()`, `nfp_resource_wait()`, and resource property accessors. Resource names include PCI vNIC resources, hwinfo, NSP, NSP diagnostics, NFFW, and MAC statistics.

## Control Flow

The header has no implementation. Consumers acquire CPP resources by name, query resource CPP ID/address/size, release resources, read hwinfo, and use NSP state helpers around management-processor operations. Resource names are fixed strings whose keys are CRC32-POSIX in the resource implementation.

## State and Persistence Behavior

The described state lives in NFP resource tables, hwinfo databases, and NSP firmware state. NSP config helpers expose mutable in-memory state for config entry iteration and modified tracking. Resource acquisition/release controls access to firmware-advertised address ranges.

## Dependencies and Integration Points

It includes `nfp_cpp.h` and is included by netdev PF probe, debugdump, ethtool NSP diagnostics, resource users, and hwinfo/NSP/resource implementation files. It bridges driver code to NFP service-processor and resource abstractions.

## Risks and Edge Cases

Resource names and CRC32 keying are ABI-sensitive. Callers must release acquired resources and handle optional resources returning `-ENOENT`. NSP config state functions expose raw pointers and indexes, so sequencing must be disciplined by the NSP implementation.

## Test Signals

Compile all nfpcore users, test resource acquire/wait/release for present and absent resources, hwinfo lookup and packed string retrieval, NSP ETH-table read/write, identify/sensor reads, and leak detection for unreleased resources.
