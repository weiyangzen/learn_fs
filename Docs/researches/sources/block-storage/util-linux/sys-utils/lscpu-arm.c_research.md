# File Research: sources/block-storage/util-linux/sys-utils/lscpu-arm.c

`lscpu-arm.c` provides ARM/aarch64 CPU implementer and part-number decoding for `lscpu`.

Key behavior:
- Contains static implementer tables mapping ARM implementer IDs to vendor names and part-number tables.
- Covers ARM, Broadcom, Cavium, Qualcomm, Samsung, NVIDIA, Marvell, Apple, Fujitsu, HiSilicon, Ampere, Microsoft, Phytium, and others.
- Detects ARM for live systems by architecture name `aarch64`; for dumps it infers ARM from known implementer IDs.
- Converts raw `/proc/cpuinfo` implementer and part fields into human-readable vendor/model strings.
- Converts ARM revision/variant into `rXpY` stepping format for ARM implementer `0x41`.
- On live aarch64 systems, supplements model/vendor/family data from DMI when available.
- Detects a special “cluster” mode for aarch64 systems without ACPI PPTT and with a single CPU type.
- Implements `--arm-id`, `--arm-id=<id>`, and `--arm-id=<id> --arm-model=<id>` output backends.

Important dependencies:
- Shared `lscpu_cxt` and `lscpu_cputype` structures from `lscpu.h`.
- `libsmartcols` for ARM implementer/model table output.
- DMI helpers from `lscpu-dmi.c`.

Risk notes:
- Tables are manually maintained and must track new ARM implementers/parts.
- `HW_IMPL_NOOVERWRITE` for Phytium intentionally avoids replacing existing `/proc/cpuinfo` vendor/model strings.
- Cluster socket counts rely on DMI when ACPI PPTT is absent, which may be missing or inaccurate.
