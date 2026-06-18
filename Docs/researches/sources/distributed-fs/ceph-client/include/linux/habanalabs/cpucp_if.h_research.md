<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/habanalabs/cpucp_if.h -->
# sources/distributed-fs/ceph-client/include/linux/habanalabs/cpucp_if.h

Purpose: This header defines the host-driver to HabanaLabs CpuCP firmware ABI for event queues, primary queue packets, sensor/hwmon requests, NIC data, memory-error reports, security attestation, and device information.

Important APIs/types/functions: It includes `hl_boot_if.h` and defines event IDs, EQ entry layouts, ECC/HBM/RAZWI/SEI/ARC/address-decoder event payloads, EQ control bit masks, PQ init statuses, a large `enum cpucp_packet_id`, packet control/result masks, `struct cpucp_packet` and variable-length packet wrappers, packet return codes, hwmon-aligned enums for temperature/voltage/current/fan/pwm/power, MSI/PLL/RL/PVT indexes, `struct cpucp_info`, NIC info/status structures, HBM row replacement data, security attestation structures, monitor dump structures, and generic passthrough subcommands.

Control flow, state, and persistence: The host writes one CpuCP packet in device memory, clears the fence, interrupts firmware, polls the fence, and reads result/output fields. EQ entries flow asynchronously from firmware to host with ready/type/index bits and fixed payload union. Device information and NIC/security data are returned into host-provided buffers sized by `data_max_size` to tolerate firmware/driver version mismatch.

Dependencies/integration: It is tightly coupled to the HabanaLabs PCI driver, firmware, hwmon, NIC management, security/TPM attestation, event queue interrupt handling, and boot interface definitions. Fields use fixed endian types because data crosses host/firmware boundaries.

Risks and test signals: ABI stability is critical: enum order comments explicitly forbid reordering MSI/PLL values. Flexible arrays and host-provided sizes must be validated to prevent firmware/driver mismatch corruption. Tests should cover packet encode/decode, fence timeout/error return codes, EQ ready/index handling, endian conversion, event payload sizing, NIC mask lengths, security buffer length fields, and compatibility with older firmware lacking newer packets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/habanalabs/cpucp_if.h -->
