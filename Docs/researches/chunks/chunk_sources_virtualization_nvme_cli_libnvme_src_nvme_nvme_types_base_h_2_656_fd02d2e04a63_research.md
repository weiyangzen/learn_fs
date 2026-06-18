# Chunk Research: sources/virtualization/nvme-cli/libnvme/src/nvme/nvme-types-base.h lines 6563-9212

## Scope

This report covers only `sources/virtualization/nvme-cli/libnvme/src/nvme/nvme-types-base.h` lines 6563-9212 in learn_fs subset A (`Docs/research_subset_a.md`). I read the requested range completely. Adjacent context was used only to identify the file-level contract (`NVMe Base Specification type definitions`, based on NVMe Base Specification 2.3) and the shared bitfield helpers `NVME_GET()` / `NVME_SET()`.

This chunk starts inside the documentation block for `enum nvme_status_field` and runs through the end of the file.

## APIs And Type Surface

The chunk is a public C header surface for libnvme's base NVMe constants, packed wire-layout structures, and inline decode helpers:

- Status API: `enum nvme_status_field` defines status code type bits, status code masks, generic status codes, command-specific status codes, command-set-specific status codes, media/data-integrity errors, path errors, and status flags (`CRD`, `MORE`, `DNR`) at lines 6774-6995. `nvme_status_code_type()` and `nvme_status_code()` extract SCT and SC from a completion status field at lines 7004-7019.
- API return status encoding: `enum nvme_status_type` reserves high bits in positive `int` returns for NVMe vs NVMe-MI status types at lines 7040-7046. `NVME_STATUS_TYPE()`, `nvme_status_get_type()`, `nvme_status_get_value()`, and `nvme_status_equals()` expose the type/value split at lines 7048-7090.
- Command and selector constants: `enum nvme_admin_opcode` covers admin opcodes, including Identify, Features, namespace management, virtualization, discovery, live migration, fabrics, format, security, sanitize, and memory-range commands at lines 7145-7196. `enum nvme_identify_cns`, `enum nvme_cmd_get_log_lid`, and `enum nvme_features_id` map Identify CNS values, log page identifiers, and feature identifiers at lines 7245-7472.
- Feature bitfield definitions: `enum nvme_feat` defines the `_SHIFT` and `_MASK` constants consumed by `NVME_GET()` / `NVME_SET()` for many feature dwords at lines 7649-7822.
- Command subfield enums: lines 7831-8369 define value enums for Get Features, Format NVM, namespace management, firmware commit, directives, sanitize, self-test, virtualization, logs, async events, fabrics, NVM I/O, and key-value opcodes.
- Namespace management data: `struct nvme_ns_mgmt_host_sw_specified` at lines 8426-8454 is a SWIG-hidden wire-layout structure for host-specified namespace creation data, including FDP and ZNS-specific fields.
- Live migration support: lines 8483-8901 define Controller Data Queue, Track Send, Migration Send, and Migration Receive command-field masks plus live-migration controller state structures.
- Feature decode helpers: lines 8903-9202 expose `NVME_FEAT_*` getter macros and `static inline` `nvme_feature_decode_*()` functions. The chunk ends with `nvme_id_ns_flbas_to_lbaf_inuse()` at lines 9207-9212.

## Control Flow

There is no runtime control flow beyond inline extraction helpers. The only branch in the chunk is `nvme_status_equals()` checking negative API return values before comparing encoded positive status type/value fields.

All other inline functions are straight-line pointer-output decoders. They do not allocate, perform I/O, lock, mutate globals, validate pointers, or convert little-endian wire fields.

## State And Dependencies

The chunk defines immutable compile-time constants and C struct layouts. Runtime state is caller-owned.

Direct dependencies are `NVME_GET()` / `NVME_SET()`, `__u*` and `__le*` typedefs from `<nvme/types.h>`, `bool`, earlier `NVME_SMART_CRIT_*` constants, and earlier `NVME_FLBAS_LOWER()` / `NVME_FLBAS_HIGHER()` helpers. Downstream consumers include `nvme-cmds-base.h` command builders and `nvme-cmds.c` feature validators.

## Risks And Invariants

The main risk is ABI and protocol drift. These values mirror NVMe specification numeric assignments; changing enum values, masks, shifts, field widths, padding, or struct ordering changes command dwords or wire layouts.

Status code values are intentionally reused across status code types, so consumers must compare both SCT and SC or use the encoded libnvme status helpers.

The status-return encoding stores a type tag in high bits of a positive signed `int`; callers must check sign before using raw extractors. Most decode helpers blindly dereference output pointers and assume host-endian feature dword inputs.

Live-migration controller state structures use zero-length arrays in a union, so consumers must compute payload offsets and sizes exactly. `struct nvme_ns_mgmt_host_sw_specified` depends on anonymous union and packed nested-struct layout compatibility.

Public spelling quirks such as `NVME_SC_INVALID_CONTROLER_DATA_QUEUE` and `nvme_feature_decode_reservation_persistance` should be treated as stable identifiers.

## Cross-Chunk References

The chunk begins mid-documentation for `enum nvme_status_field`; the start of that comment and earlier status-code context are in the previous chunk. Earlier chunks also define the file-level helper macros, Identify namespace bitfield helpers, SMART critical warning bits, and FLBAS masks consumed here.

This chunk reaches the end of `nvme-types-base.h`, so there is no later chunk for this file.