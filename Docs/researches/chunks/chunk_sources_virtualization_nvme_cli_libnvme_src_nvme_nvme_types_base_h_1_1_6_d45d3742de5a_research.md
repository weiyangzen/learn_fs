# Chunk Research: sources/virtualization/nvme-cli/libnvme/src/nvme/nvme-types-base.h lines 1-6562

## Scope

This chunk is the first 6,562 lines of `libnvme`'s NVMe base-specification type header. It is in subset A because `sources/virtualization/nvme-cli` is part of the virtualization/block-device integration source trees in `Docs/research_subset_a.md`.

The chunk is declaration-heavy C API surface: constants, bitfield helpers, controller register layouts, Identify data structures, log page structures, feature payloads, asynchronous event codes, and the beginning of status-code documentation. There is almost no runtime control flow beyond four small inline helpers.

## APIs and Declarations

### Public bitfield helper API

- Lines 40-41 define UUID sizing constants.
- Lines 54-107 define the central field extraction and construction macros: `NVME_GET`, `NVME_SET`, `NVMF_GET`, `NVMF_SET`, `NVME_CHECK`, and `NVME_VAL`.
- These macros are the foundation for nearly every `NVME_*()` accessor macro in this chunk.

### Global NVMe constants and command-set IDs

- `enum nvme_constants` at lines 161-192 defines sentinel IDs and fixed transfer/list limits: namespace sentinels, identify transfer size `4096`, list maximums, telemetry block size `512`, NQN/fabrics address limits, ZNS changed-zone limit, and stream ID max.
- `enum nvme_csi` at lines 202-208 declares command set indicators for NVM, KV, ZNS, subsystem local memory, and computational programs.

### Controller register model

- `enum nvme_register_offsets` at lines 243-272 maps controller BAR0/property offsets for CAP, VS, CC, CSTS, queue registers, CMB, boot partition, CRTO, and PMR registers.
- `nvme_is_64bit_reg()` at lines 286-298 classifies known 64-bit registers.
- Register bitfield enums and accessors cover CAP, VS, CC, CSTS, AQA/ASQ/ACQ, CMB, boot partition, CRTO, and PMR fields.
- Inline helpers compute CMB size, PMR size, PMR throughput, and power scale from encoded fields.

### Identify and log structures

- `struct nvme_id_ctrl` at lines 1548-1677 models the 4096-byte Identify Controller payload, including PCI/vendor identity, controller capabilities, admin/NVM/fabrics support, namespace limits, ANA, HMB, sanitize, power measurement, and power state descriptors.
- `struct nvme_id_ns` at lines 2801-2845 models Identify Namespace data: capacity/use counters, LBA formats, metadata/protection settings, reservations, ANA group, NVM set/endurance group IDs, NGUID/EUI64, and vendor bytes.
- Identify-list structures cover NVM set lists, UUID list, controller list, namespace list, domain list, endurance group list, and supported log pages.
- Log/event structures include error log, SMART log, firmware slot, command effects, self-test, telemetry, endurance group, ANA, persistent events, LBA status, boot partition, sanitize status, power measurement, host metadata, streams directives, HMB attributes, async events, and pull-model DDC request log.

### Status-code continuation

- Lines 6264-6562 begin the documentation block for `enum nvme_status_field`.
- The actual enum declaration and numeric status definitions continue in the next chunk, so this chunk only contains the visible documentation for many generic, media, path, queue, firmware, feature, namespace-management, sanitize, KV, and FDP status meanings.

## Control Flow

There is no command execution, I/O, allocation, or mutable control loop in this chunk. Control flow consists only of small inline helpers:

- `nvme_is_64bit_reg()` switch dispatch.
- `nvme_cmb_size()` arithmetic.
- `nvme_pmr_size()` arithmetic.
- `nvme_pmr_throughput()` arithmetic.
- `nvme_psd_power_scale()` bit shifting.

All other behavior is compile-time structure layout and preprocessor macro expansion.

## State and Data Model

The chunk models host-visible NVMe device state rather than maintaining library state:

- Controller register state: CAP, VS, CC, CSTS, queue base addresses, CMB/PMR/boot-partition registers, and ready-timeout fields.
- Identify state: controller capabilities, namespace geometry, namespace formats, controller/namespace/domain/endurance lists, and command-set support.
- Health and telemetry state: SMART counters, endurance group health, telemetry logs, persistent events, sanitize state, power measurements, LBA status, EOM, reachability, and media unit configuration.
- Feature state payloads: APST, host metadata, LBA range type, predictable latency mode, host behavior, streams directive, identify directives, and HMB attributes.

Data is wire-format oriented: fixed-width `__u8`/`__le16`/`__le32`/`__le64` types, explicit reserved padding, 128-bit values as byte arrays, flexible/zero-length arrays for variable payloads, and selected `__attribute__((packed))` records.

## Dependencies

- Standard headers: `<stdbool.h>`, `<stdint.h>`, and `<stdio.h>`.
- Local/libnvme dependency: `<nvme/types.h>`, providing NVMe fixed-width and little-endian aliases.
- Later chunks provide the rest of `enum nvme_status_field`, command structures, command opcodes, feature identifiers, and additional helpers referenced by comments or fields.
- Comments reference other NVMe concepts such as `nvme_trtype`, `NVME_FEAT_FID_*`, `NVME_LOG_LID_*`, fabrics/discovery constructs, and command-specific CDW layouts.

## Risks and Edge Cases

- Macro correctness is critical because most field accessors expand through `NVME_GET`.
- Suspicious accessor definitions visible in this chunk:
  - Line 1034: `NVME_PMRSWTP_PMRSWTV(pmrswtp)` extracts `PMRSWTP_PMRSWTU`, not `PMRSWTP_PMRSWTV`.
  - Line 1965: `NVME_CTRL_CRCAP_RGICS(crcap)` references `CTRL_CRCAP_RGICS`, but the enum defines `RGIDC`.
  - Lines 2135-2146: `NVME_CTRL_OACS_*` macros call `NVME_GET()` without passing the `oacs` value argument.
- `NVME_SET()` and `NVMF_SET()` cast values to `__u32`, which is risky if reused for wider fields.
- Flexible and zero-length arrays require callers to validate external log lengths before indexing.
- `struct nvme_nss_hw_err_event` contains a host pointer, unlike most wire-format structs, so raw persistent-event bytes cannot be safely overlaid onto it.
- Nested variable records require parser logic based on counts/lengths, not `sizeof`.
- Packed structs may cause unaligned member access issues on strict-alignment architectures.
- GNU C extensions are used: `__attribute__((packed))` and zero-length arrays.

## Cross-Chunk References

- The file continues beyond line 6562. This chunk ends inside the documentation block for `enum nvme_status_field`; the enum declaration and numeric values are expected in chunk 2.
- Later chunks likely consume the constants, structs, and naming conventions established here for command CDWs, status decoding, and feature/log definitions.
- The structs declared here are likely used by libnvme command wrappers and nvme-cli commands for Identify, Get Log Page, Get/Set Features, telemetry, sanitize, and event-log operations.

## Research Notes

- Read scope: `Docs/research_subset_a.md`.
- Read source range completely: `sources/virtualization/nvme-cli/libnvme/src/nvme/nvme-types-base.h` lines 1-6562.
- Wrote the chunk report to `Docs/researches/chunks/chunk_sources_virtualization_nvme_cli_libnvme_src_nvme_nvme_types_base_h_1_1_6_d45d3742de5a_research.md`.
- Did not create or modify the final per-file report.