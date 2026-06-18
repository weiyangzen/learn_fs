# sources/distributed-fs/ceph-client/include/linux/firmware/xlnx-zynqmp-crypto.h

## Purpose
This header exposes Xilinx/AMD secure firmware crypto calls for ZynqMP and Versal platforms, including AES engine operation, SHA hashing, feature selection, and Versal AES-GCM staged operations.

## APIs, types, and control flow
`struct xlnx_feature` maps platform family and feature id to device data. `XSECURE_API_*` constants identify AES firmware commands. When ZynqMP firmware is reachable, callers can invoke `zynqmp_pm_aes_engine(address, out)`, `zynqmp_pm_sha_hash(address, size, flags)`, feature-data lookup, and Versal AES operations: key write/zero, operation init, AAD update, encrypt/decrypt update, finalization, and initialization. Without firmware, functions return `-ENODEV` or `ERR_PTR(-ENODEV)`.

## State and dependencies
State is mostly firmware-resident. Callers pass DMA/physical addresses containing request structures and buffers; key state may persist in secure hardware until zeroed. The header relies on ZynqMP firmware reachability and common error-pointer handling.

## Integration, risks, and tests
Crypto drivers and firmware-backed secure services integrate here. Risks include passing non-DMA-safe addresses, wrong request structure layout, key lifetime leaks, treating `ERR_PTR` as data, and missing feature gating by family. Tests should cover disabled stubs, key zero after use, AES staged sequencing, SHA size/flag validation, firmware error propagation, and feature map lookup for each supported family.
