# sources/distributed-fs/ceph-client/drivers/mtd/parsers/qcomsmempart.c

Purpose: Qualcomm SMEM-backed flash partition parser. It reads a shared-memory partition table provided by firmware and creates MTD partitions from block offsets.

Important APIs/types/functions: `parse_qcomsmem_part()` is the parser entry for `qcom,smem-part`. `struct smem_flash_ptable` and `struct smem_flash_pentry` model SMEM table versions 3 and 4. `parse_qcomsmem_cleanup()` frees dynamically duplicated names.

Control flow: the parser rejects NOR devices when 4 KiB sectors are configured because SMEM tables use eraseblock units. It first reads only the header via `qcom_smem_get()`, validates magic, partition count, and version, calculates the full table length, then reads the complete table. It counts non-empty names, allocates exactly that many `mtd_partition` entries, lowercases duplicated names, and converts offset/length from eraseblock units to bytes.

State and persistence: partition definitions persist in Qualcomm SMEM, not in the flash being parsed. Runtime state consists of allocated partition names and array. The cleanup callback owns those names. No flash writes occur.

Dependencies and integration: depends on Qualcomm SMEM service ID 9 in host 0, MTD erase size, ctype lowercasing, and parser OF matching. Risks include SMEM probe deferral, version drift beyond v4, attr-to-`mask_flags` semantic assumptions, multiplication overflow on large devices, and incompatibility with 4 KiB-sector NOR. Test signals include v3/v4 tables, empty names, uppercase names, excessive partition count, invalid magic/version, `-EPROBE_DEFER`, and cleanup leak checks.
